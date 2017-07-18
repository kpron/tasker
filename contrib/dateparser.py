def parsetype(duestring):
    if duestring.startswith("+"):
        return "plus"
    elif duestring[0].isdigit():
        return "spec"

def timecalc(pretime):
    if len(pretime) == 1:
        return int(pretime[0])
    elif len(pretime) == 2:
        return (int(pretime[0]) * 60) + int(pretime[1])
    elif len(pretime) == 3:
        return (int(pretime[0]) * 1440) + (int(pretime[1]) * 60) + int(pretime[2])
    else:
        return int(0)

def dateparse(duestring):
    duetype = parsetype(duestring)
    if duetype == "plus":
        pretime = duestring[1:].split(".")
        return timecalc(pretime)
    else:
        print("not support")

