#coding=utf-8
'''
Created on 2014��3��20��

@author: cc
'''

import os

counter = 1
def print_to_file(file_name, page):
    '''
    This function is for testing
    '''
    global counter
    my_file = open('./data/'+str(file_name) + str(counter) + ".html", 'w')
    
    counter += 1
    
    my_file.write(str(page) + os.linesep)
    my_file.close()

def print_dom_tree_recursive(tree, depth):
    for i in range(1,depth):
        print '   ',
    for child in tree:
        print child.tag 
        print_dom_tree_recursive(child, depth+1)
        
def print_dom_tree(tree):
    print_dom_tree_recursive(tree, 0)

if __name__ == "__main__":
    import logging
    import logging.config
    
    logging.config.fileConfig('runtime_infor_log.conf')
    
    logger = logging.getLogger('proxyLog')
    
    logger.info("for test")
