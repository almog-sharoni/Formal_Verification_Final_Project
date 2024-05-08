read_model -i sokoban.smv
# BDD solver
#go
c#heck_ltlspec

# SAT solver
go_bmc
check_ltlspec_bmc -k 100

quit



