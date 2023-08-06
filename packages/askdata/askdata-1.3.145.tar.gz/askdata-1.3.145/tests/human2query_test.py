from askdata.human2query import nl2query

if __name__ == "__main__":
    nl = "goals of Cristiano Ronaldo from {{timePeriod.A}}"
    smartquery, version = nl2query(nl, language="en-US")
    print(smartquery)
    print(version)
