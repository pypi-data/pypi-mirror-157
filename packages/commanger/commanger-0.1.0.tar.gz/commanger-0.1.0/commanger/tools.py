import sys
import colorama as cr
cr.init(autoreset=True)
class subCommanger:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.cfig = {}
    def command(self, funct):
        pass
class commanger:
    def __init__(self, globe=__name__):
        self.name = globe
        self.cfig = {}
    class ArgumentError(Exception):
        pass
    class ArgumentTypeError(Exception):
        pass
    def basicCfig(self, l: list, bl=True):
        """
        Form a basic config and set commanger.cfig to the output unless bl = False.
        
        Returns: config dict
        
        Example:
        `cmd.basicCfig([1, 2, '3', 'four'])`
        Goes to:
        ```python
        {1: {'type': 'pos', 'in': [None], 'pos': 1, 'base': None}, 2: {'type': 'pos', 'in': [None], 'pos': 2, 'base': None}, '3': {'type': 'tg', 'base': False}, 'four': {'type': 'ltg', 'base': False}}
        ```
        """
        if type(l) != list:
            error = "Arg is not list"
            raise TypeError(error)
        ps = 1
        cfigg = {}
        
        l = sorted(l, key=lambda val: str(val))
        for x in l:
            
            if type(x) is int:
                cfigg[x] = {
                    "type": "pos",
                    "in": [None],
                    "pos": ps,
                    "base": None
                }
            elif type(x) is str and len(x) == 1:
                cfigg[x] = {
                    "type": "tg",
                    
                    "base": False
                }
            elif type(x) is str:
                cfigg[x] = {
                    "type": "ltg",
                    
                    "base": False
                }
            ps += 1
        if bl:
            self.cfig = cfigg
        return cfigg
    def __enter__(self):
        raise NotImplementedError(" ")
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError(" ")
    def config(self, config=None):
        """
        Get a pretty version of commanger.cfig or supplied config
        
        Returns: string
        """
        if config==None:
            n = self.cfig
        else:
            n = config
        out = "{\n"
        for x in n.keys():
            out = out + f"\n\t{cr.Fore.LIGHTGREEN_EX}" + str(x) + cr.Fore.WHITE+": {\n"
            for y in n[x].keys():
                out = out + f"\t\t{cr.Fore.LIGHTGREEN_EX}" + str(y) + f"{cr.Fore.WHITE}: {cr.Fore.LIGHTBLUE_EX}" + str(n[x][y]) +f"{cr.Fore.WHITE},\n"
            out = out + "\t}, \n"
        out = out+"\n}\n"
        return out
    def evalArgs(self, args):
        """
        Dev funct evalArgs:
        Evaluates args.
        """
        
        
        def indexExists(list,index):
            if 0 <= index < len(list):
                return True
            else:
                return False
        o = {}
        i = 1
        c = self.cfig
        for k in c.keys():
            
            if c[k]["type"] == "pos":
                if not indexExists(args, c[k]["pos"]):
                    error = f"Arg number {c[k]['pos']} is not in {args}"
                    raise self.ArgumentError(error)
                if not c[k]["in"] == [None]:
                    if not type(args[i]) in c[k]["in"]:
                        error = f"Expected type {c[k]['type']}, got type {type(args[i])}"
                        raise self.ArgumentTypeError(error)
                o[str(i)] = args[i]
                i += 1
            elif c[k]["type"] == "tg":
                if f"-{k}" in args[i:]:
                    o[k] = not c[k]["base"]
                else:
                    o[k] = c[k]["base"]
            elif c[k]["type"] == "ltg":
                if f"--{k}" in args[i:]:
                    o[k] = not c[k]["base"]
                else:
                    o[k] = c[k]["base"]
        return o
        
    def command(self, funct):
        """
        Funct that runs on command. Key function. It is recommended to have only one of commanger.command and commanger.commandU
        
        Returns: None
        
        Expect: A dict as the single argument

        Example:
        ```python
        @commanger.command
        def main(args):
            #do stuff
        ```
        """
        e = self.evalArgs(sys.argv)
        funct(e)
    def commandU(self, funct):
        """
        Funct that runs on command. Key function. It is recommended to have only one of commanger.command and commanger.commandU
        
        Returns: None
        
        Expect: **kwargs as arguments.

        Examples:
        ```python
        @commanger.commandU
        def main(**kwargs): #get as dict
            #do stuff
        ```
        ```python
        @commanger.commandU
        def main(*, hi, bye, hello): #get as individual args
            #do stuff
        ```        
        """
        e = self.evalArgs(sys.argv)
        
        funct(**e)

    def subCommand(self, name):
        return subCommanger(self, name)
        