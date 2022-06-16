import two_way_net_2_gmns as tg

two_way_node_filename = 'input_node.csv'
two_way_link_filename = 'input_link.csv'

# convert 2-way network to 1 way network
tg.convert_node_to_gmns(two_way_node_filename, node_id='ID', x_coord='Longitude',
                        y_coord='Latitude', zone_id='CentroidNode')
ab_list = ["AB CAP"]
ba_list = ["BA CAP"]

tg.convert_link_to_gmns(two_way_link_filename, \
                        link_id='ID', from_node_id='From ID', to_node_id='To ID', dir_flag='Dir', \
                        ab_length='Length', ba_length='Length', ab_lanes='AMLANESAB', ba_lanes='AMLANESBA', \
                        ab_speed='AB SPEED', \
                        ba_speed='BA SPEED', FT='FT', AT='AT', link_type='link_type', ab_list=ab_list, \
                        ba_list=ba_list, keep_original_attributes=True)
