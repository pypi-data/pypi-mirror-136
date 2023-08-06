import Rahimcalc as r
def main():
    a=sys.argv[1]
    b=sys.argv[2]
    c=sys.argv[3]
    if a=='sum':
        r.sum(b,c)
    if a=='sub':
        r.sub(b,c)
    if a=='mul':
        r.mul(b,c)
    if a=='div':
        r.div(b,c)
    if a=='exp':
        r.exp(b,c)
    if a=='complex':
        r.complex(b,c)
if __name__=='__main__':
    main()
