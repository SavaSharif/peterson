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
        N = self.processes
        for i in range(self.processes):
            dst = src.clone()
            proc = dst.process[i]

            if proc.pc == 0:
                if dst.level[i] < N - 1:
                    proc.pc = 1
                    yield (dst, self.actions["for-level(%d)" % i])
                else:  # exit loop
                    proc.pc = 10
                    yield (dst, self.actions["for-level(%d)" % i])

            elif proc.pc == 1:
                dst.last[dst.level[i]] = i
                proc.pc = 2
                yield (dst, self.actions["set-last(%d)" % i])

            elif proc.pc == 2:
                if proc.k < N:
                    proc.pc = 3
                    yield (dst, self.actions["for-k(%d)" % i])
                else:  # exit loop
                    proc.k = 0
                    proc.pc = 8
                    yield (dst, self.actions["for-k(%d)" % i])

            elif proc.pc == 3:
                if proc.k == i:
                    proc.k += 1
                    proc.pc = 2
                    yield (dst, self.actions["if-ki(%d)" % i])
                else:  # enter wait state
                    proc.pc = 5
                    yield (dst, self.actions["if-ki(%d)" % i])

            elif proc.pc == 5:
                if dst.last[dst.level[i]] != i or dst.level[proc.k] < dst.level[i]:  # wait until
                    proc.pc = 6
                yield (dst, self.actions["await(%d)" % i])

            elif proc.pc == 6:
                proc.k += 1
                proc.pc = 2
                yield (dst, self.actions["for-k(%d)" % i])

            elif proc.pc == 8:
                dst.level[i] += 1
                proc.pc = 0
                yield (dst, self.actions["for-level(%d)" % i])

            elif proc.pc == 10:
                proc.pc = 11
                yield (dst, self.actions["enter-cs(%d)" % i])

            elif proc.pc == 11:
                # critical section
                dst.level[i] = 0
                proc.pc = 0
                yield (dst, self.actions["exit-cs(%d)" % i])

            """
            0: for level[i] from 0 to (N - 1):
            1:     last[level[i]] := i;
            2:     for k from 0 to N:
            3:         if k==i: continue;
            4:         await last[level[i]]!=i or level[k] < level[i];
            5: nop;
            6: level[i] := 0; goto 0;
            """

            """
            Flattened version of pseudocode above, used for logic of program
            0:  if level[i] < N - 1:
            1:      last[level[i]] := i;
            2:      if k < N:
            3:         if k==i: 
            4:              k++; goto 2; 
            5:         await last[level[i]]!=i or level[k] < level[i];
            6:         k++;
            7:         goto 2;
            8:      level[i]++;
            9:      goto 0;
            10:  nop;
            11:  level[i] := 0; goto 0;
            """
        return


def main():
    # create a 3-process Peterson model
    mdl = Model(3)

    count = 0
    mutual = True
    deadlocks = 0
    for s in mdl.reach():
        count += 1
        if((count % 1000) == 0):
            print(count)

        if len(s.labels) > 1:
            mutual = False

        successors = mdl.nextStates(s)

        try:
            next(successors)
        except StopIteration:
            deadlocks += 1

    print("%d reachable states" % count)
    if not mutual:
        print("Mutual exclusion is not satisfied.")
    print("%d deadlocks" % deadlocks)
    pass


if(__name__ == "__main__"):
    main()
