from argparse import Action
import model


class State(model.State):
    """
    State for a Peterson model [model].
    """
    __slots__ = ["process", "level", "last"]

    class Process(object):
        __slots__ = ["pc", "k"]

        def __init__(self, pc=0, k=0):
            self.pc = pc
            self.k = k

        def __repr__(self):
            return "Process(pc = %d, k = %d)" % (self.pc, self.k)

        def clone(self):
            return State.Process(self.pc, self.k)

    def __init__(self, model):
        super().__init__(model)
        self.process = tuple(State.Process() for _ in range(model.processes))
        self.level = [0] * model.processes
        self.last = [0] * (model.processes - 1)

    def __repr__(self):
        tmp = (self.process, self.level, self.last)
        return "State(%s,\n level = %s, last = %s)" % tmp

    def __iter__(self):
        for proc in self.process:
            yield proc.pc
            yield proc.k
        for i in self.level:
            yield i
        for i in self.last:
            yield i

    def clone(self):
        """
        Returns a copy of this state that may be modified.
        """
        s = State.__new__(State)
        super(State, s).__init__(self.model)

        s.process = tuple(proc.clone() for proc in self.process)
        s.level = self.level[:]
        s.last = self.last[:]
        return s

    @property
    def labels(self):
        """
        Returns a set of all state labels applicable in this state.
        """
        labels = set()
        for i, proc in enumerate(self.process):
            if(proc.pc == 5):
                labels.add("proc %d in CS" % i)

        mdl = self.model
        return {mdl.labels[v] for v in labels}


class Model(model.Model):
    """
    Peterson model with [n] processes.
    """
    name = "Peterson"

    def __init__(self, n=3):
        super().__init__()

        self.processes = n
        self.initialState = State(self)

        for i in range(self.processes):
            # create actions
            self.actions.add("for-level(%d)" % i)
            self.actions.add("set-last(%d)" % i)
            self.actions.add("for-k(%d)" % i)
            self.actions.add("if-ki(%d)" % i)
            self.actions.add("await(%d)" % i)
            self.actions.add("enter-cs(%d)" % i)
            self.actions.add("exit-cs(%d)" % i)

            # create labels
            self.labels.add("proc %d in CS" % i)

    def nextStates(self, src: State):
        """
        Returns for each successor state of [src] a tuple consisting of the
         state object and the action used to get there.
        """
        for i in range(self.processes):
            dst = src.clone()
            # proc = dst.process[i]
            # actions = self.actions

            # for l in range(self.processes - 1):
            #     dst.level[i] = l
            #     dst.last[l] = i
            #     while dst.last[l] == i and any(dst.level[k] >= l for k in range(self.processes) if k != i):
            #         continue
            # # begin critical section
            # # end critical section

            # dst.level[i] = -1
            # yield dst, self.actions["cri"]

            for l in range(self.processes - 1):
                dst.level[i] = l
                dst.last[l] = i
                for k in range(self.processes):
                    if k == i:
                        continue
                    while True:
                        if dst.last[l] != i or dst.level[k] < l:
                            break

            # begin critical section
            # end critical section

            dst.level[i] = -1
            yield dst, self.actions

            """
            0: for level[i] from 0 to (N - 1):
            1:     last[level[i]] := i;
            2:     for k from 0 to N:
            3:         if k==i: continue;
            4:         await last[level[i]]!=i or level[k] < level[i];
            5: nop;
            6: level[i] := 0; goto 0;
            """
            # actions = self.actions["action-name"]

            """
            TODO (Peterson lab): implement the body of the next-state function.
            `dst` is a copy of the state vector; modify it and yield a
            tuple(dst, action).

            The Action objects can be retrieved using
            `self.actions["action-name"]`.
            """

        return dst, None


def main():
    # create a 3-process Peterson model
    mdl = Model(3)

    count = 0
    for s in mdl.reach():
        count += 1
        if((count % 1000) == 0):
            print(count)

        """
        TODO (Peterson lab): implement a check for mutual exclusion.
        """

        """
        TODO (Peterson lab): implement a check for deadlocks.
        """

    print("%d reachable states" % count)
    pass


if(__name__ == "__main__"):
    main()
