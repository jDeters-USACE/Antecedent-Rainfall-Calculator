# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

######################################
##  ------------------------------- ##
##       watershed_summary.py       ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import time
import datetime

# Import 3rd Party Libraries
import numpy
import matplotlib.pyplot as plt
import pylab



def parse_results(results_list):
    parse_result = []
    # List Red coloration items
    red_items = [
        "Dry Season",
        'Mild drought',
        'Moderate drought',
        'Severe drought',
        'Extreme drought'
    ]
    # Define colors for cell color matrices
    light_green = (0.5, 0.8, 0.5)
    light_blue = (0.4, 0.5, 0.8)
    light_red = (0.8, 0.5, 0.5)
    light_grey = (0.85, 0.85, 0.85)
    white = (1, 1, 1)
    black = (0, 0, 0)
    pie_red = '#ff9999'
    pie_green = '#99ff99'
    pie_blue = '#66b3ff'
    pie_orange = '#ffcc99'
    # Get Numbers of each Main APT Condition and all APT Values
    antecedent_precipitation_score_sum = 0
    num_wet = 0
    num_normal = 0
    num_dry = 0
    num_total = 0
    for result_tuple in results_list:
        # Add current antecedent_precipiation_score
        antecedent_precipitation_score_sum += result_tuple[0]
        num_total += 1
        if result_tuple[1] == 'Wetter than Normal':
            num_wet += 1
        elif result_tuple[1] == 'Normal Conditions':
            num_normal += 1
        elif result_tuple[1] == 'Drier than Normal':
            num_dry += 1
    # Find average antecedent_precipitation_score
    average_antecedent_precipitation_score = round((antecedent_precipitation_score_sum / num_total), 2)
    # Determine name and color of Preliminary Decision
    if average_antecedent_precipitation_score < 10:
        preliminary_determination = "Drier than Normal"
        preliminary_determination_color = light_red
    elif average_antecedent_precipitation_score >= 10 and average_antecedent_precipitation_score < 15:
        preliminary_determination = 'Normal Conditions'
        preliminary_determination_color = light_green
    elif average_antecedent_precipitation_score >= 15:
        preliminary_determination = 'Wetter than Normal'
        preliminary_determination_color = light_blue
    # Get percentages for each AP Class for Pie Chart
    pie_sizes = []
    pie_labels = []
    pie_colors = []
    if num_wet > 0:
        wet_percent = round((num_wet / num_total), 2)
        pie_sizes.append(wet_percent)
        pie_labels.append('Wetter than Normal')
        pie_colors.append(pie_blue)
    if num_normal > 0:
        normal_percent = round((num_normal / num_total), 2)
        pie_sizes.append(normal_percent)
        pie_labels.append('Normal Conditions')
        pie_colors.append(pie_green)
    if num_dry > 0:
        dry_percent = round((num_dry / num_total), 2)
        pie_sizes.append(dry_percent)
        pie_labels.append('Drier than Normal')
        pie_colors.append(pie_red)
    # Get unique set of result conditions
    results_set = list(set(results_list))
    # Sort results by ap score
    results_set.sort(key=lambda x: x[0], reverse=True)
    # Determine frequency of each unique condition set
    sampling_points_table_values = []
    sampling_points_table_colors = []
    # Add First row of values and colors
    sampling_points_table_values.append([
        'Antecedent Precipitation Score',
        'Antecedent Precipitation Condition',
        r"WebWIMP H$_2$O Balance",
        'Drought Index (PDSI)',
        '# of Points'])
    sampling_points_table_colors.append([light_grey, light_grey, light_grey, light_grey, light_grey])
    for result_tuple in results_set:
        # Get count of unique list's occurance
        count = results_list.count(result_tuple)
        result_list = list(result_tuple)
        # Add occurance to end of list
        final_list = result_list + [count]
        # Append list to sampling_points_table_values
        sampling_points_table_values.append(final_list)
        # Create color row for sampling_points_table_colors
        color_row = []
        # Determine which color to add for each item in row
        for item in final_list:
            # Can't say "if item in red_items because some PDSI values
            #  are marked with (2011-11) or similar indications that they
            #  are using the previous month's PDSI Value, so we'll work
            red = False
            for red_item in red_items:
                if red_item in str(item):
                    red = True
                    break
            if red is True:
                color_row.append(light_red)
            else:
                color_row.append(white)
        # Append color row to sampling_points_table_colors
        sampling_points_table_colors.append(color_row)
    # Add items to result list
    parse_result.append(average_antecedent_precipitation_score)
    parse_result.append(preliminary_determination)
    parse_result.append(preliminary_determination_color)
    parse_result.append(pie_sizes)
    parse_result.append(pie_labels)
    parse_result.append(pie_colors)
    parse_result.append(sampling_points_table_values)
    parse_result.append(sampling_points_table_colors)
    return parse_result

        

def create_summary(site_lat, site_long, observation_date, geographic_scope, huc, huc_size, results_list, watershed_summary_path):
    """Creates Summary of results and prints to pdf"""
    # Define Colors
    light_grey = (0.85, 0.85, 0.85)
    white = (1, 1, 1)

    # Parse results list using function
    parsed_results = parse_results(results_list)
    
    # Unpack function results
    avg_ap_score = parsed_results[0]
    preliminary_determination = parsed_results[1]
    preliminary_determination_color = parsed_results[2]
    pie_sizes = parsed_results[3]
    pie_labels = parsed_results[4]
    pie_colors = parsed_results[5]
    sampling_points_table_values = parsed_results[6]
    sampling_points_table_colors = parsed_results[7]
    
    # Construct Figure
    #plt.ion() # MAKES PLOT.SHOW() NON-BLOCKING
    fig = plt.figure(figsize=(15, 8.5))
    fig.set_facecolor('0.90')
    ax1 = plt.subplot2grid((20, 9), (3, 1), colspan=4, rowspan=2)
    ax2 = plt.subplot2grid((20, 9), (6, 1), colspan=4, rowspan=2)
    ax3 = plt.subplot2grid((20, 9), (9, 1), colspan=4, rowspan=2)
    ax4 = plt.subplot2grid((20, 9), (12, 0), colspan=9, rowspan=9)
    ax5 = plt.subplot2grid((20, 9), (3, 5), colspan=2, rowspan=7)

    #pie_colors = [light_red, light_green, light_blue]
    patchyes, texts, autotexts = ax5.pie(pie_sizes,
                                        colors=pie_colors,
                                        labels=pie_labels,
                                        autopct='%1.1f%%',
                                        shadow=True,
                                        startangle=90)
#    for text in texts:
#        text.set_color('grey')
#    for autotext in autotexts:
#        autotext.set_color('grey')
#     Equal aspect ratio ensures that pie is drawn as a circle
#    ax4.axis('equal')

    # Remove axis from subplots (For displaying tables)
    ax1.axis('off')
    ax2.axis('off')
    ax3.axis('off')
    ax4.axis('off')
    ax5.axis('off')
    ax1.axis('tight')
    ax2.axis('tight')
    ax3.axis('tight')
    ax4.axis('tight')
    ax5.axis('tight')

    # Add Axis Titles
    fig.suptitle('Antecedent Precipitation Tool - Watershed Sampling Summary', fontsize=17)
    ax1.set_title('User Inputs')
    ax2.set_title('Intermediate Data')
    ax3.set_title('Preliminary Result')
    ax4.set_title('Sampling Point Breakdown')

    # Create Inputs Table
    inputs_table_values = [
        ['Coordinates', '{}, {}'.format(round(float(site_lat), 6), round(float(site_long), 6))],
        ['Date', observation_date],
        ['Geographic Scope', geographic_scope]
    ]

    # Create Inputs Table Colors
    inputs_table_colors = [
        [light_grey, white],
        [light_grey, white],
        [light_grey, white]
    ]

    # Plot inputs_table
    inputs_table = ax1.table(cellText=inputs_table_values,
                            cellColours=inputs_table_colors,
                            colWidths=[0.25, 0.355],
                            cellLoc='center',
                            loc='lower center')

    inputs_table.auto_set_font_size(False)
    inputs_table.set_fontsize(12)
    inputs_table.scale(1, 1)

    # Create Intermediate Data Table
    num_sampling_points = len(results_list)
    intermediate_table_values = [
        ['Hydrologic Unit Code', huc],
        ['Watershed Size', r'{} mi$^2$'.format(huc_size)],
        ['# Random Sampling Points', num_sampling_points]
    ]

    # Create Intermediate Data Table Colors
    intermediate_table_colors = [
        [light_grey, white],
        [light_grey, white],
        [light_grey, white]
    ]

    # Plot intermediate_data_table
    intermediate_data_table = ax2.table(cellText=intermediate_table_values,
                                        cellColours=intermediate_table_colors,
                                        colWidths=[0.355, 0.22],
                                        cellLoc='center',
                                        loc='lower center')
    intermediate_data_table.auto_set_font_size(False)
    intermediate_data_table.set_fontsize(12)
    intermediate_data_table.scale(1, 1)

    # Create Preliminary Determination Table
    prelim_determ_table_values = [
        ['Average Antecedent Precipitation Score', avg_ap_score],
        ['Preliminary Determination', preliminary_determination]
    ]

    # Create Preliminary Determination Table Colors
    prelim_determ_table_colors = [
        [light_grey, white],
        [light_grey, preliminary_determination_color]
    ]

    # Plot preliminary determination table
    prelim_determ_table = ax3.table(cellText=prelim_determ_table_values,
                                    cellColours=prelim_determ_table_colors,
                                    colWidths=[0.53, 0.265],
                                    cellLoc='center',
                                    loc='center')
    prelim_determ_table.auto_set_font_size(False)
    prelim_determ_table.set_fontsize(12)
    prelim_determ_table.scale(1, 1)

    # Plot Sampling Points Breakdown Table
    sampling_point_table = ax4.table(cellText=sampling_points_table_values,
                                    cellColours=sampling_points_table_colors,
                                    colWidths=[0.19, 0.21, 0.145, 0.175, 0.09],
                                    cellLoc='center',
                                    loc='upper center')
    sampling_point_table.auto_set_font_size(False)
    sampling_point_table.set_fontsize(12)
    sampling_point_table.scale(1, 1)

    # Get string of today's date
    today_datetime = datetime.datetime.today()
    today_str = today_datetime.strftime('%Y-%m-%d')
    # Add Generated on today's date text
    date_generated_text = ax1.text(0.027, 0.153, "Generated on {}".format(today_str), size=10)

    # Remove space between subplots
    plt.subplots_adjust(wspace=0.00,
                        hspace=0.00,
                        left=0.00,
                        bottom=0.00,
                        top=1.00,
                        right=1.00)

    if watershed_summary_path is None:
        # Display Figure
        plt.show()
        time.sleep(1)
    else:
        # Save PDF
        print('Saving Watershed Summary figure...')
        fig.savefig(watershed_summary_path, facecolor='0.90')
    
        # Closing figure in memory safe way
        print('Closing figure...')
        pylab.close(fig)
        print('')
        return True


if __name__ == '__main__':
    RESULTS_LIST = [
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)")
    ]


    create_summary(site_lat="38.4008283",
                   site_long="-120.8286800",
                   observation_date="2020-02-10",
                   geographic_scope='HUC8 Watershed',
                   huc='180400120000',
                   huc_size=1266.29,
                   results_list=RESULTS_LIST,
                   watershed_summary_path=None)

#                   watershed_summary_path=r'C:\Users\L2RCSJ9D\Desktop\Antecedent\Rainfall\~HUC\8\18040012\2020-02-10 - HUC 18040012 - Summary.pdf')
