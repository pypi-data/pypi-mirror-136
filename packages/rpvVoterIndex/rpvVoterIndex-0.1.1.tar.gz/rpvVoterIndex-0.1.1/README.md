Voter Power Indexes
======

Vote Power Index provides tools to run both Banzhaf Power Index and Shapley–Shubik Index to analyse 2 party poltical geographies like US Congresstional Districts to see if the reapproation process maintained Mintorities communties to elect their candidate of choice

# Usage
> power_index(df, OtherPopCol, TargetPopCol, Party1, Party2, vIndex=None, filename=None)

## Parameters 

df - Pandas Dataframe

OtherPopCol - Majority community 

TargetPopCol - Minority community

OtherParty - None colitlition party of choice

ColilitionParty - Colitlition party of choice

vIndex (ssi/bpi/none): 
- **None** both indexes 
- **ssi** Shapley–Shubik Index
- **bpi** Banzhaf Power Inde

filename - optional