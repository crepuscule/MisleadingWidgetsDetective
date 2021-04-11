# 当前地址为input_data
find . -name *.abandon > abandon_list.txt
# vim abandon_list.txt
# ctrl+v copy
# %s/^/mv /g
# %s/.abandon$//g
