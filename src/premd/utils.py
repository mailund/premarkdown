"""Various functions that do not belong anywhere else but are
useful in several modules."""

import collections

def merge_dicts(to_dict, from_dict):
    """"Merge :from_dict into :to_dict, overwriting where
they share keys."""
    for key, val in from_dict.items():
    	# if we have a dict in both to and from dict, merge them
        if (key in to_dict and isinstance(to_dict[key], dict) 
        	and isinstance(val, collections.Mapping)):
            merge_dicts(to_dict[key], val)
        else:
        	# if we do not know the key already, or 
        	# if we override it with something that is not
        	# a dict, simply overwrite
            to_dict[key] = val
