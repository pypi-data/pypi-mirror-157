import datetime
import logging
import threading
import time
from collections import OrderedDict
from functools import wraps
from typing import Dict, Iterable, List, Optional

import binsync.data
from binsync.core.client import Client, SchedSpeed
from binsync.data import (Comment, Enum, Function, GlobalVariable,
                          StackVariable, Struct, User)

_l = logging.getLogger(name=__name__)


#
# State Checking Decorators
#


def init_checker(f):
    @wraps(f)
    def initcheck(self, *args, **kwargs):
        if not self.check_client():
            raise RuntimeError("Please connect to a repo first.")
        return f(self, *args, **kwargs)

    return initcheck


def make_state(f):
    """
    Build a writeable State instance and pass to `f` as the `state` kwarg if the `state` kwarg is None.
    Function `f` should have have at least two kwargs, `user` and `state`.
    """

    @wraps(f)
    def state_check(self, *args, **kwargs):
        state = kwargs.pop('state', None)
        user = kwargs.pop('user', None)
        if state is None:
            state = self.client.get_state(user=user)

        kwargs['state'] = state
        r = f(self, *args, **kwargs)
        self.client.commit_state(state, msg=self._generate_commit_message(f, *args, **kwargs))
        return r

    return state_check


def make_state_with_func(f):
    @wraps(f)
    def _make_state_with_func(self, *args, **kwargs):
        state: binsync.State = kwargs.pop('state', None)
        user = kwargs.pop('user', None)
        if state is None:
            state = self.client.get_state(user=user)

        # a comment
        if "func_addr" in kwargs:
            func_addr = kwargs["func_addr"]
            if func_addr and not state.get_function(func_addr):
                state.functions[func_addr] = Function(func_addr, self.get_func_size(func_addr))
        # a func_header or stack_var
        else:
            func_addr = args[0]
            if not state.get_function(func_addr):
                state.functions[func_addr] = Function(func_addr, self.get_func_size(func_addr))

        kwargs['state'] = state
        r = f(self, *args, **kwargs)
        self.client.commit_state(state, msg=self._generate_commit_message(f, *args, **kwargs))
        return r

    return _make_state_with_func


def make_ro_state(f):
    """
    Build a read-only State _instance and pass to `f` as the `state` kwarg if the `state` kwarg is None.
    Function `f` should have have at least two kwargs, `user` and `state`.
    """

    @wraps(f)
    def state_check(self, *args, **kwargs):
        state = kwargs.pop('state', None)
        user = kwargs.pop('user', None)
        if state is None:
            state = self.client.get_state(user=user)
        kwargs['state'] = state
        kwargs['user'] = user
        return f(self, *args, **kwargs)

    return state_check


#
# Description Constants
#

# https://stackoverflow.com/questions/10926328
BUSY_LOOP_COOLDOWN = 0.5


class SyncControlStatus:
    CONNECTED = 0
    CONNECTED_NO_REMOTE = 1
    DISCONNECTED = 2


class SyncLevel:
    OVERWRITE = 0
    NON_CONFLICTING = 1
    MERGE = 2


#
#   Controller
#

class BinSyncController:
    """
    The BinSync Controller is the main interface for syncing with the BinSync Client which preforms git tasks
    such as pull and push. In the Controller higher-level tasks are done such as updating UI with changes
    and preforming syncs and pushes on data users need/change.

    All class properties that have a "= None" means they must be set during runtime by an outside process.
    The client will be set on connection. The ctx_change_callback will be set by an outside UI

    """
    def __init__(self, headless=False, reload_time=10):
        self.headless = headless
        self.reload_time = reload_time

        # client created on connection
        self.client = None  # type: Optional[Client]

        # ui callback created on UI init
        self.ui_callback = None  # func()
        self.ctx_change_callback = None  # func()
        self._last_reload = None
        self.last_ctx = None

        # settings
        self.sync_level: int = SyncLevel.NON_CONFLICTING

        # command locks
        self.queue_lock = threading.Lock()
        self.cmd_queue = OrderedDict()

        # create a pulling thread, but start on connection
        self.updater_thread = threading.Thread(target=self.updater_routine)

    #
    #   Multithreading updaters, locks, and evaluators
    #

    def make_controller_cmd(self, cmd_func, *args, **kwargs):
        with self.queue_lock:
            self.cmd_queue[time.time()] = (cmd_func, args, kwargs)

    def _eval_cmd(self, cmd):
        # parse the command if present
        if not cmd:
            return

        func, f_args, f_kargs = cmd[:]
        func(*f_args, **f_kargs)

    def _eval_cmd_queue(self):
        with self.queue_lock:
            if not self.cmd_queue:
                return

            job_count = 1
            jobs = [
                self.cmd_queue.popitem(last=False)[1] for _ in range(job_count)
            ]

        for job in jobs:
            self._eval_cmd(job)

    def updater_routine(self):
        while True:
            time.sleep(BUSY_LOOP_COOLDOWN)

            # validate a client is connected to this controller (may not have remote )
            if not self.check_client():
                continue

            # do git pull/push operations if a remote exist for the client
            if self.client.has_remote:
                if self.client.last_pull_attempt_ts is None:
                    self.client.update(commit_msg="User created")

                # update every reload_time
                elif time.time() - self.client.last_pull_attempt_ts > self.reload_time:
                    self.client.update()

            if not self.headless:
                # update context knowledge every loop iteration
                if self.ctx_change_callback:
                    self._check_and_notify_ctx()

                # update the control panel with new info every BINSYNC_RELOAD_TIME seconds
                if self._last_reload is None or \
                        time.time() - self._last_reload > self.reload_time:
                    self._last_reload = time.time()
                    self._update_ui()

            # evaluate commands started by the user
            self._eval_cmd_queue()

    def _update_ui(self):
        if not self.ui_callback:
            return

        self.ui_callback()

    def start_updater_routine(self):
        self.updater_thread.setDaemon(True)
        self.updater_thread.start()

    def _check_and_notify_ctx(self):
        active_ctx = self.active_context()
        if active_ctx is None or self.last_ctx == active_ctx:
            return

        self.last_ctx = active_ctx
        self.ctx_change_callback()

    #
    # Client Interaction Functions
    #

    def connect(self, user, path, init_repo=False, remote_url=None):
        binary_hash = self.binary_hash()
        self.client = Client(
            user, path, binary_hash, init_repo=init_repo, remote_url=remote_url
        )

        _l.info("Starting the updater thread in the controller")
        self.start_updater_routine()
        return self.client.connection_warnings

    def check_client(self):
        return self.client is not None

    def status(self):
        if self.check_client():
            if self.client.has_remote:
                return SyncControlStatus.CONNECTED
            return SyncControlStatus.CONNECTED_NO_REMOTE
        return SyncControlStatus.DISCONNECTED

    def status_string(self):
        stat = self.status()
        if stat == SyncControlStatus.CONNECTED:
            return f"<font color=#1eba06>{self.client.master_user}</font>"
        elif stat == SyncControlStatus.CONNECTED_NO_REMOTE:
            return f"<font color=#e7b416>{self.client.master_user}</font>"
        else:
            return "<font color=#cc3232>Disconnected</font>"

    def toggle_headless(self):
        self.headless = not self.headless

    @init_checker
    def users(self, priority=None) -> Iterable[User]:
        return self.client.users(priority=priority)

    def usernames(self, priority=None) -> Iterable[str]:
        for user in self.users(priority=priority):
            yield user.name

    #
    # Override Mandatory Functions
    #

    def binary_hash(self) -> str:
        """
        Returns a hex string of the currently loaded binary in the decompiler. For most cases,
        this will simply be a md5hash of the binary.

        @rtype: hex string
        """
        raise NotImplementedError

    def active_context(self) -> binsync.data.Function:
        """
        Returns an binsync Function. Currently only functions are supported as current contexts.
        This function will be called very frequently, so its important that its implementation is fast
        and can be done many times in the decompiler.
        """
        raise NotImplementedError

    def binary_path(self) -> Optional[str]:
        """
        Returns a string that is the path of the currently loaded binary. If there is no binary loaded
        then None should be returned.

        @rtype: path-like string (/path/to/binary)
        """
        raise NotImplementedError

    def get_func_size(self, func_addr) -> int:
        """
        Returns the size of a function

        @param func_addr:
        @return:
        """
        raise NotImplementedError

    def goto_address(self, func_addr) -> None:
        """
        Relocates decompiler display to provided address

        @param func_addr:
        @return:
        """
        raise NotImplementedError

    #
    # Fillers
    #

    @init_checker
    @make_ro_state
    def fill_struct(self, struct_name, user=None, state=None):
        """
        Fill a single specific struct from the user

        @param struct_name:
        @param user:
        @param state:
        @return:
        """
        raise NotImplementedError

    @init_checker
    @make_ro_state
    def fill_structs(self, user=None, state=None):
        """
        Grab all the structs from a specified user, then fill them locally

        @param user:
        @param state:
        @return:
        """
        raise NotImplementedError

    @init_checker
    @make_ro_state
    def fill_global_var(self, var_addr, user=None, state=None):
        """
        Grab a global variable for a specified address and fill it locally

        @param var_addr:
        @param user:
        @param state:
        @return:
        """
        raise NotImplementedError

    @init_checker
    @make_ro_state
    def fill_global_vars(self, user=None, state=None):
        for off, gvar in state.global_vars.items():
            self.fill_global_var(off, user=user, state=state)

        return True

    @init_checker
    @make_ro_state
    def fill_enum(self, enum_name, user=None, state=None):
        """
        Grab an enum and fill it locally

        @param enum_name:
        @param user:
        @param state:
        @return:
        """

    @init_checker
    @make_ro_state
    def fill_enums(self, user=None, state=None):
        """
        Grab all enums and fill it locally

        @param user:
        @param state:
        @return:
        """

    @init_checker
    @make_ro_state
    def fill_function(self, func_addr, user=None, state=None):
        """
        Grab all relevant information from the specified user and fill the @func_adrr.
        """
        raise NotImplementedError

    def fill_functions(self, user=None, state=None):
        change = False
        for addr, func in state.functions.items():
            change |= self.fill_function(addr, user=user, state=state)

        return change

    @init_checker
    @make_ro_state
    def fill_all(self, user=None, state=None):
        """
        Connected to the Sync All action:
        syncs in all the data from the targeted user

        TODO:
        - add support for enums

        @param user:
        @param state:
        @param no_functions:
        @return:
        """
        _l.info(f"Filling all data from user {user}...")

        fillers = [
            self.fill_structs, self.fill_enums, self.fill_global_vars
        ]

        for filler in fillers:
            filler(user=user, state=state)

    @init_checker
    def magic_fill(self, preference_user=None):
        """
        Traverses all the data in the BinSync repo, starting with an optional preference user,
        and sequentially merges that data together in a non-conflicting way. This also means that the prefrence
        user makes up the majority of the initial data you sync in.

        This process supports: functions (header, stack vars), structs, and global vars
        TODO:
        - support for comments
        - support for enums
        - refactor fill_function to stop attempting to set master state after we do
        -

        @param preference_user:
        @return:
        """

        _l.info(f"Staring a magic sync with a preference for {preference_user}")
        # re-order users for the prefered user to be at the front of the queue (if they exist)
        all_users = list(self.usernames(priority=SchedSpeed.FAST))
        preference_user = preference_user if preference_user else self.client.master_user
        all_users.remove(preference_user)
        master_state = self.client.get_state(user=self.client.master_user, priority=SchedSpeed.FAST)

        #
        # structs
        #

        _l.info(f"Magic Syncing Structs...")
        pref_state = self.client.get_state(user=preference_user, priority=SchedSpeed.FAST)
        for struct_name in self.get_all_changed_structs():
            _l.info(f"Looking at strunct {struct_name}")
            pref_struct = pref_state.get_struct(struct_name)
            for user in all_users:
                user_state = self.client.get_state(user=user, priority=SchedSpeed.FAST)
                user_struct = user_state.get_struct(user)

                if not user_struct:
                    continue

                if not pref_struct:
                    pref_struct = user_struct.copy()
                    continue

                pref_struct = Struct.from_nonconflicting_merge(pref_struct, user_struct)
                pref_struct.last_change = None

            if pref_struct:
                master_state.structs[struct_name] = pref_struct

            self.fill_struct(struct_name, state=master_state)
        self.client.commit_state(master_state, msg="Magic Sync Structs Merged")

        #
        # functions
        #

        master_state = self.client.get_state(user=self.client.master_user, priority=SchedSpeed.FAST)

        _l.info(f"Magic Syncing Functions...")
        pref_state = self.client.get_state(user=preference_user, priority=SchedSpeed.FAST)
        for func_addr in self.get_all_changed_funcs():
            _l.info(f"Looking at func {hex(func_addr)}")
            pref_func = pref_state.get_function(addr=func_addr)
            for user in all_users:
                user_state = self.client.get_state(user=user, priority=SchedSpeed.FAST)
                user_func = user_state.get_function(func_addr)

                if not user_func:
                    continue

                if not pref_func:
                    pref_func = user_func.copy()
                    continue

                pref_func = Function.from_nonconflicting_merge(pref_func, user_func)
                pref_func.last_change = None

            master_state.functions[func_addr] = pref_func
            self.fill_function(func_addr, state=master_state)

        self.client.commit_state(master_state, msg="Magic Sync Funcs Merged")

        #
        # global vars
        #

        _l.info(f"Magic Syncing Global Vars...")
        master_state = self.client.get_state(user=self.client.master_user, priority=SchedSpeed.FAST)
        pref_state = self.client.get_state(user=preference_user, priority=SchedSpeed.FAST)
        for gvar_addr in self.get_all_changed_global_vars():
            pref_gvar = pref_state.get_global_var(gvar_addr)
            for user in all_users:
                user_state = self.client.get_state(user=user, priority=SchedSpeed.FAST)
                user_gvar = user_state.get_global_var(gvar_addr)

                if not user_gvar:
                    continue

                if not pref_gvar:
                    pref_gvar = user_gvar.copy()
                    continue

                pref_gvar = GlobalVariable.from_nonconflicting_merge(pref_gvar, user_gvar)
                pref_gvar.last_change = None

            master_state.global_vars[gvar_addr] = pref_gvar
            self.fill_global_var(gvar_addr, state=master_state)

        self.client.commit_state(master_state, msg="Magic Sync Global Vars Merged")
        _l.info(f"Magic Syncing Completed!")

    #
    # Pushers
    #

    @init_checker
    @make_state
    def push_comment(self, *args, user=None, state=None, **kwargs):
        raise NotImplementedError

    @init_checker
    @make_state_with_func
    def push_function_header(self, *args, user=None, state=None, **kwargs):
        raise NotImplementedError

    @init_checker
    @make_state_with_func
    def push_stack_variable(self, *args, user=None, state=None, **kwargs):
        raise NotImplementedError

    @init_checker
    @make_state
    def push_struct(self, *args, user=None, state=None, **kwargs):
        raise NotImplementedError

    @init_checker
    @make_state
    def push_global_var(self, *args, user=None, state=None, **kwargs):
        raise NotImplementedError

    @init_checker
    @make_state
    def push_enum(self, *args, user=None, state=None, **kwargs):
        raise NotImplementedError

    #
    # Pullers
    #

    @init_checker
    @make_ro_state
    def pull_function(self, func_addr, user=None, state=None) -> Optional[Function]:
        if not func_addr:
            return None

        return state.get_function(func_addr)

    @init_checker
    @make_ro_state
    def pull_stack_variables(self, func_addr, user=None, state=None) -> Dict[int, StackVariable]:
        return state.get_stack_variables(func_addr)

    @init_checker
    @make_ro_state
    def pull_stack_variable(self, func_addr, offset, user=None, state=None) -> StackVariable:
        return state.get_stack_variable(func_addr, offset)

    @init_checker
    @make_ro_state
    def pull_func_comments(self, func_addr, user=None, state=None) -> Dict[int, Comment]:
        return state.get_func_comments(func_addr)

    @init_checker
    @make_ro_state
    def pull_comment(self, addr, user=None, state=None) -> Comment:
        return state.get_comment(addr)

    @init_checker
    @make_ro_state
    def pull_comments(self, user=None, state=None) -> Comment:
        return state.comments()

    @init_checker
    @make_ro_state
    def pull_struct(self, struct_name, user=None, state=None) -> Struct:
        return state.get_struct(struct_name)

    @init_checker
    @make_ro_state
    def pull_structs(self, user=None, state=None) -> List[Struct]:
        """
        Pull structs downwards.

        @param user:
        @param state:
        @return:
        """
        return state.get_structs()

    @init_checker
    @make_ro_state
    def pull_global_var(self, addr, user=None, state=None) -> GlobalVariable:
        return state.get_global_var(addr)

    @init_checker
    @make_ro_state
    def pull_enum(self, enum_name, user=None, state=None) -> Enum:
        return state.get_enum(enum_name)

    @init_checker
    @make_ro_state
    def pull_enums(self, user=None, state=None) -> List[Enum]:
        return state.get_enums()

    #
    # Utils
    #

    def generate_func_for_sync_level(self, sync_func: Function) -> Function:
        if self.sync_level == SyncLevel.OVERWRITE:
            return sync_func

        master_state = self.client.get_state()
        master_func = master_state.get_function(sync_func.addr)
        if not master_func:
            return sync_func

        if self.sync_level == SyncLevel.NON_CONFLICTING:
            new_func = Function.from_nonconflicting_merge(master_func, sync_func)

        elif self.sync_level == SyncLevel.MERGE:
            _l.warning("Manual Merging is not currently supported, using non-conflict syncing...")
            new_func = Function.from_nonconflicting_merge(master_func, sync_func)

        else:
            raise Exception("Your BinSync Client has an unsupported Sync Level activated")

        return new_func

    @staticmethod
    def get_default_type_str(size):
        if size == 1:
            return "unsigned char"
        elif size == 2:
            return "unsigned short"
        elif size == 4:
            return "unsigned int"
        elif size == 8:
            return "unsigned long long"
        else:
            raise Exception("Unable to decide default type string!")

    def _generate_commit_message(self, pusher, *args, **kwargs):
        from_user = kwargs.get("user", None)
        msg = "Synced " if from_user else "Updated "

        if pusher.__qualname__ == self.push_function_header.__qualname__:
            addr = args[0]
            sync_type = "function"
            sync_data = hex(addr)
        elif pusher.__qualname__ == self.push_comment.__qualname__:
            addr = args[0]
            sync_type = "comment"
            sync_data = hex(addr)
        elif pusher.__qualname__ == self.push_stack_variable.__qualname__:
            func_addr = args[0]
            offset = args[1]
            sync_type = "stack_var"
            sync_data = f"{hex(offset)}@{hex(func_addr)}"
        elif pusher.__qualname__ == self.push_struct.__qualname__:
            struct_name = args[0].name
            sync_type = "struct"
            sync_data = struct_name
        else:
            sync_type = ""
            sync_data = ""

        msg += f"{sync_type}:{sync_data}"
        msg += f"from {from_user}" if from_user else ""
        if not sync_data:
            msg = "Generic Update"
        return msg

    def get_all_changed_funcs(self):
        known_funcs = set()
        for username in self.usernames(priority=SchedSpeed.FAST):
            state = self.client.get_state(user=username, priority=SchedSpeed.FAST)
            for func_addr in state.functions:
                known_funcs.add(func_addr)

        return known_funcs

    def get_all_changed_structs(self):
        known_structs = set()
        for username in self.usernames(priority=SchedSpeed.FAST):
            state = self.client.get_state(user=username, priority=SchedSpeed.FAST)
            for struct_name in state.structs:
                known_structs.add(struct_name)

        return known_structs

    def get_all_changed_global_vars(self):
        known_gvars = set()
        for username in self.usernames(priority=SchedSpeed.FAST):
            state = self.client.get_state(user=username, priority=SchedSpeed.FAST)
            for offset in state.global_vars:
                known_gvars.add(offset)

        return known_gvars
