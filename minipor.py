import model;
import model.slotState;

import model.reduction;

class State(model.slotState.SlotState):
    @property
    def labels(self):
        """
        Returns a set of all state labels applicable in this state.
        """
        labels = set();

        labels.add("pcA==%d" % self["pcA"]);
        labels.add("pcB==%d" % self["pcB"]);

        if(self["y"]==3):
            labels.add("y==3");

        mdl = self.model;
        return {mdl.labels[v] for v in labels};

class Model(model.Model):
    """
    POR toy problem model object.

    This model is the "Commutativity is Not Enough" example used in the lecture
     about Partial Order Reduction.
    """
    name = "Mini POR model";
    def __init__(self):
        super().__init__();

        s = ["pcA", "pcB", "a", "x", "y"];
        self.initialState = State(self, s);

        self.actions.update({
            "a = 0": {
                "guards": ["pcA==0"],
                "DNA": ["a = 0", "y = 2", "await (y==3)"],
                "reads":  [],
                "writes": ["pcA", "a"],
            },
            "y = 2": {
                "guards": ["pcA==1"],
                "DNA": ["a = 0", "y = 2", "await (y==3)", "y = 3"],
                "reads":  [],
                "writes": ["pcA", "y"],
            },
            "await (y==3)": {
                "guards": ["pcA==2", "y==3"],
                "DNA": ["a = 0", "y = 2", "await (y==3)"],
                "reads":  [],
                "writes": [],
            },
            "x = 1": {
                "guards": ["pcB==0"],
                "DNA": ["x = 1", "y = 3"],
                "reads":  [],
                "writes": ["pcB", "x"],
            },
            "y = 3": {
                "guards": ["pcB==1"],
                "DNA": ["y = 2", "x = 1", "y = 3"],
                "reads":  [],
                "writes": ["pcB", "y"],
            },
        });

        self.labels.update({
            "pcA==0": {
                "NES": [],
                "tests": ["pcA"],
            },
            "pcA==1": {
                "NES": ["a = 0"],
                "tests": ["pcA"],
            },
            "pcA==2": {
                "NES": ["y = 2"],
                "tests": ["pcA"],
            },
            "pcB==0": {
                "NES": [],
                "tests": ["pcB"],
            },
            "pcB==1": {
                "NES": ["x = 1"],
                "tests": ["pcB"],
            },
            "pcB==2": {
                "NES": ["y = 3"],
                "tests": ["pcB"],
            },
            "y==3": {
                "NES": ["y = 2", "y = 3"],
                "tests": ["y"],
            },
        });

    def nextStates(self, src):
        # first process
        dst = src.clone();
        if(src["pcA"]==0):
            dst["pcA"] = 1;
            dst["a"] = 0;
            yield (dst, self.actions["a = 0"]);

        elif(src["pcA"]==1):
            dst["pcA"] = 2;
            dst["y"] = 2;
            yield (dst, self.actions["y = 2"]);

        elif(src["pcA"]==2 and dst["y"]==3):
            yield (dst, self.actions["await (y==3)"]);

        # second process
        dst = src.clone();
        if(src["pcB"]==0):
            dst["pcB"] = 1;
            dst["x"] = 1;
            yield (dst, self.actions["x = 1"]);

        elif(src["pcB"]==1):
            dst["pcB"] = 2;
            dst["y"] = 3;
            yield (dst, self.actions["y = 3"]);

def main():
    mdl = Model();

    # regular reachability
    print("%d states" % sum(1 for _ in mdl.reach()));

    # reachability with POR
    por = model.reduction.POR(mdl);
    print("%d states w/ POR" % sum(1 for _ in por.reach()));

if(__name__=="__main__"):
    main();
