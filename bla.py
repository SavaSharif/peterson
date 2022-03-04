"""
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
11:  level[i] := 0;
12:  goto 0;
"""
