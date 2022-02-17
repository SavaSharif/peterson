import ast;

from . import util;

class Tokenizer(util.Tokenizer):
    """
    Tokenizer object.
    """
    _tokens = [
        ("_",         r"[ \t\r\n]+"),
        ("KEYWORD",   r"not|and|or|until|release|next|finally|globally"
                       + r"|true|false|[()]"),
        ("PREDICATE", r"[_A-Za-z][_0-9A-Za-z]*|\"(\\.|[^\"])*\""),
        ("INVALID",   r"[^ \t]+")
    ];

class Parser(util.Parser):
    """
    LL(1) parser object.
    """
    # keep ordered s.t. FIRST sets/nullable can be determined in one pass
    _rules = [
        ("#expr-primary", "true"),
        ("#expr-primary", "false"),
        ("#expr-primary", "PREDICATE"),
        ("#expr-primary", "(", "#expr", ")"),

        ("#expr-unary", "#expr-primary"),
        ("#expr-unary", "not", "#expr-unary"),
        ("#expr-unary", "next", "#expr-unary"),
        ("#expr-unary", "finally", "#expr-unary"),
        ("#expr-unary", "globally", "#expr-unary"),

        ("#expr-binary'",),
        ("#expr-binary'", "and", "#expr-binary"),
        ("#expr-binary'", "or", "#expr-binary"),
        ("#expr-binary'", "until", "#expr-binary"),
        ("#expr-binary'", "release", "#expr-binary"),
        ("#expr-binary", "#expr-unary", "#expr-binary'"),

        ("#expr", "#expr-binary"),

        ("#^", "#expr", None)
    ];

    def __init__(self, src):
        super().__init__(src);

    def parse(self):
        """
        Parse an LTL expression.
        Returns the parsed Expression.
        """
        stack = [];
        for rule, match in super().parse():
            head = rule[0].name;
            if(head=="#expr-primary"):
                if(len(rule)==2):
                    # <expr-primary> := ...
                    m = match[0];
                    if(m[0]=="\""):
                        m = ast.literal_eval(m);

                    stack.append(Expression("value", m));
                else:
                    # <expr-primary> := ( <expr> )
                    pass;

            elif(head=="#expr-binary'"):
                if(len(rule)==1):
                    # <expr-binary'> := ε
                    stack.append(None);
                else:
                    # <expr-binary'> := binary-op ...
                    stack.append(Expression(match[0], None, stack.pop()));

            elif(head=="#expr-binary"):
                # <expr-binary> := <expr-primary> <expr-binary'>
                expr = stack.pop();
                if(expr is not None):
                    assert(expr.args[0] is None);
                    stack.append(Expression(expr.op, stack.pop(),
                                            expr.args[1]));

            elif(head=="#expr-unary" and len(rule) > 2):
                # <expr-unary> := unary-op ...
                stack.append(Expression(match[0], stack.pop()));

        assert(len(stack)==1);
        return stack[-1];

class Expression(object):
    """
    LTL expression object. Expressions are kept in negation normal form.
    """
    exprs = {};

    def __new__(cls, *args):
        op = args[0];
        if(op=="not" and (args[1].op!="value" or args[1]._negate is not None)):
            # push NOT operator inward
            return ~args[1];

        elif(op=="finally"):
            return Expression("until", Expression.TRUE, args[1]);

        elif(op=="globally"):
            return Expression("release", Expression.FALSE, args[1]);

        # ensure only one of each Expression
        if(args not in Expression.exprs):
            Expression.exprs[args] = super().__new__(cls);

        return Expression.exprs[args];

    def __init__(self, op, *args):
        if(hasattr(self, "op")):
            return;

        self.op = op;
        self.args = list(args);

        self._negate = None;
        if(self.op=="not"):
            assert(self.args[0]._negate is None);
            self._negate = self.args[0];
            self.args[0]._negate = self;

    def __repr__(self):
        if(self.op=="value"):
            return repr(self.args[0]);

        if(len(self.args)==1):
            return "%s %s" % (self.op, self.args[0]);

        o = " %s " % self.op;
        o = o.join(repr(v) for v in self.args);
        return "(%s)" % o;

    _dual = {
        "next": "next",
        "and": "or",
        "or": "and",
        "until": "release",
        "release": "until",
    };

    def __invert__(self):
        if(self._negate is not None):
            return self._negate;

        neg = None;
        if(self.op=="value"):
            # only introduce NOT before terminals
            neg = Expression("not", self);

        elif(self.op=="not"):
            # NOT operators have _negate set on init
            assert(False);

        elif(self.op in self._dual):
            neg = Expression(self._dual[self.op], *(~a for a in self.args));

        else:
            raise NotImplementedError;

        self._negate = neg;
        return self._negate;

# set up boolean literals
Expression.TRUE = Expression("value", "true");
Expression.FALSE = Expression("value", "false");
Expression.TRUE._negate = Expression.FALSE;
Expression.FALSE._negate = Expression.TRUE;

def parse(s):
    return Parser(Tokenizer(s)).parse();
