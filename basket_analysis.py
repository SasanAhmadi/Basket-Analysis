import argparse
import csv
import gzip
import sys
import os
import tempfile
import shutil
from itertools import combinations

# This is the main function which calculates the number of occurances for each product combination, 
# Number of items in combinations is variable
def analyze_basket(data_file_path, output_file_path, number_of_items_in_combinations):
    # Local variables to hold items in each iteration
    current_basket_Id = 0
    basket_content = []

    # Indicator for displaying progress, the progres report is static for 2000 baskets1
    marker = 0
    
    try:
        print('Start reading baskets')
        with tempfile.TemporaryDirectory() as tmpdirname:           # Create a temporary directory to hold intermediate files
            with gzip.open(data_file_path, 'rt') as f:              # Use GZip to open file - based on sample I assumed using GZip for reading instead of extracting the file
                reader = csv.reader(f, delimiter=',')
                for row in reader:
                    if current_basket_Id != row[0]:                 # If line moved to another basket then reset local variables
                        marker +=1                                  # increase the status marker
                        if (marker % 2000) == 0:
                            print('[{0}] Baskets read...\r'.format(marker), end = '')           # Report progress per 2000 basket read
                        
                        # Create a file for every basket after reading its entire content(products withiin the basket)
                        write_basket(tmpdirname, current_basket_Id, basket_content, number_of_items_in_combinations)
                        
                        # Refresh local variables to hold new basket data
                        current_basket_Id = row[0]
                        basket_content = []

                    # Store product from basket
                    basket_content.append(row[1])
                else:
                    # Create the last file when loop ends
                    write_basket(tmpdirname, current_basket_Id, basket_content, number_of_items_in_combinations)

            print('Total number of baskets read: ' + str(marker))

            result = {}              # Create a dictionary to hold the combination and its occurance

            marker = 0               # Zero the counter for progress report

            print ('Begin analyzing combinations')
            
            # Iterate through each basket file 
            for f in os.scandir(tmpdirname):
                marker+=1
                if (marker % 2000) == 0:
                    print('[{0}] Baskets analyzed...\r'.format(marker), end = '')
                
                with open(f.path) as basket:
                    # Iterate combination within the basket file 
                    for line in basket:
                        if not line.rstrip() in result.keys():          # Add the combination if it was not already in dictionary
                            result[line.rstrip()] = 1
                        else:
                            result[line.rstrip()] +=1                   # Add to the occurance of the existing combination 
        print('Total number of baskets (more than {0} items) analyzed: '.format(number_of_items_in_combinations) + str(marker))
        print ('Writing result file')

        # Write the result to the CSV file, 
        # csv file writer not used becuase it was a simple write without any complexity,
        # Also the first items (product ids) are already comma separated
        with open(output_file_path, 'w', newline='') as output_file:
            for k,v in result.items():
                output_file.write(k + ',' + str(v) + '\n')

        print('Finished.')
    except:
        print('Generating the dataset did not work: {0}'.format(err))

# This will writes intermediate files for each basket 
# containing each possible combination of prducts inside the basket
# number_of_items_in_combinations --> this will determin how many items are we intersted in a combination
def write_basket(tmep_dir_name, basket_id, basket_content, number_of_items_in_combinations):
    #if number of products in the basket is less than the number of combinations ignore the basket
    if basket_content != [] and len(basket_content) >= number_of_items_in_combinations:         
        #create a file with name eual to basket_Id
        with open('{0}\{1}.txt'.format(tmep_dir_name, basket_id), 'w') as f:
            # this will sort the items by productId inside the basket 
            # and uses the itertool.combinations to create possible combinations for given number of items per combination
            # because of sorting there will be always a predictable way of seeing combinations among baskets
            # otherwise there could be replaceable order of product ids
            # example : 
            #    ordered_basket(1,2,3) --combination of 2--> [(1,2),(1,3),(2,3)]        this is what algorythm expects
            #    UNORDERED_basket(2,3,1) --combination of 2--> [(2,3),(2,1),(3,1)]      this will create different keys for different baskets, 
            #                                                        if we use order it will be the same rule for all
            for item in combinations(sorted(basket_content),number_of_items_in_combinations):
                f.write('{0}\n'.format(','.join(item)))

if __name__ == '__main__':
    # Define arguments
    parser = argparse.ArgumentParser(description='Analyze basket data.')


    parser.add_argument('--data_file_path', type=str, 
                        help='path to the source csv GZip file')
    parser.add_argument('--output_file_path', type=str, 
                        help='output csv file to store the result(it will override the file if existed)')
    parser.add_argument('--number_of_items_in_combinations', type=int, default=2,   
                        help='Number of combinations to search in baskets')
    args = parser.parse_args()

    # Check if the source file exists and has a GZip file extension
    if args.data_file_path == None:
        raise Exception('Argument data_file_path  not provided!')
    if not os.path.exists(args.data_file_path):
        raise Exception(args.data_file_path + ' -- Does not exists!')
    elif not args.data_file_path.endswith('.gz'):
        raise Exception(args.data_file_path + ' -- Is not a GZip file extension!')

    # Check if output_file_path has been provided
    if args.output_file_path == None:
        raise Exception('Argument output_file_path  not provided!')

    # Try to create the output file (Check for possible problems such as access level)
    try:
        basedir = os.path.dirname(args.output_file_path)
        if basedir != '' and not os.path.exists(basedir):
            os.makedirs(basedir)
        open(args.output_file_path, 'w').close()
    except:
        raise Exception(args.data_file_path + ' -- Could not create the output file!')

    # Check if number of combinations is greater than or equal 2
    if args.number_of_items_in_combinations < 2:
        raise Exception('Numbe of combinations must be greater than 2')

    # Call to the processing function
    analyze_basket(args.data_file_path, args.output_file_path, args.number_of_items_in_combinations)
