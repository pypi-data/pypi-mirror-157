from askdata import Askdata
from askdata.human2query import smartner

if __name__ == "__main__":

    # Login
    user = Askdata(domainlogin="askdata", env="dev")
    token = user.get_token()

    # Get datasets
    workspace = "askdatacovid_2"
    agent = user.agent(slug=workspace)
    df_datasets = agent.list_datasets()
    datasets = df_datasets['id'].values.tolist()

    # Usage
    nl = "deaths in Italy"
    smartquery_list = smartner(nl, token=token, workspace=workspace, datasets=datasets, language="en-US")
    for sq in smartquery_list:
        print(sq)
        print("#")
