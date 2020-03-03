The goal is to compute from sales data how often product combinations of any
two products are bought within the same basket. The sales data consists of a CSV file with
multiple baskets, where each basket contains at least one product that was bought. 

An example of a file with 3 baskets:

|-----------+------------|
| basket_id | product_id |
|-----------+------------|
| 123       | 1		 |
| 123       | 2		 |
| 456       | 1		 |
| 456       | 2		 |
| 456       | 3 	 |
| 789       | 1 	 |
|-----------+------------|

Which should result in the following output of the implemented algorithm:

|-----------+-----------+-----------|
| product_1 | product_2 | # baskets |
|-----------+-----------+-----------|
| 1 	    | 2         | 2         |
| 2         | 3         | 1         |
| 1         | 3         | 1         |
|-----------+-----------+-----------|

I.e. both products 1 and 2 were bought in the two baskets 123 and 456, which is why the
result for this combination is two. The product combination 1 and 3, as well as 2 and 3,
appear only in basket 456, and therefore their result is one. The basket 789 contains only
one product and therefore does not change the result at all.

Some further notes:
- the order of the rows in the result output doesn’t matter.
- the results for product combinations like (1, 2) and (2, 1) are always identical. 
- a product will appear at most once in each basket.
- each basket will only have a small number of products, and all products of a basket will appear within consecutive lines of the input file.


Restrictions

The main challenge is that neither the input file nor
the output file fit into memory. Therefore the calculation will imply some intermediate steps:
- somehow split the dataset into multiple smaller datasets.
- compute intermediate results for each of the smaller datasets.
- combine the intermediate results to create the final result.
