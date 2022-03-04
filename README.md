## 1 Peterson’s algorithm

Sava Sharif - s2685612

### 1.1 Task 1

The program graph could be optimized by combining states, but for me this representation made most sense. The conditions and actions taken are represented in the program graph. The critical state is S11 in the program graph.

![Program graph](/program_graph.jpg)

### 1.2 Task 2

A state has labels when it is in the critical section. In order to check whether the program satisfies mutual exclusion, it counts the number of states with labels, indicating they are in the critical section. If there is more than one process in the critical section, it will print that mutual exclusion is not satisfied. In my case, there is a fault somewhere causing mutual exclusion to not be satisfied. I could not find the cause of this.

### 1.3 Task 3

To check whether deadlocks occur, all successors are retrieved of the reachable states. If the state does not have a successor, it indicates a deadlock. The program prints the number of deadlocks.
