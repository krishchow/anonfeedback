#!/bin/bash

# To be run on mcs. Assumes all posts have a subject including "Feedback Responses" and are written by Petersen.
mysql mcs_bb -u peters43 -p <<< "select * from mcs_bb_posts where subject like '%Feedback Responses%' and username='peters43';" > posts.tsv
