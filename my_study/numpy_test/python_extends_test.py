# -*- coding: utf-8 -*-
'''
Created on Jan 22, 2016

@author: nlp
'''







class BaseClass():
    
    def __init__( self, name, age ):
        self.name = name
        self.age = age
    
    def talk( self ):
        print "base talk", self.name, self.age
        
        
class SubClass( BaseClass ):
    
    def __init__( self, name, age, height ):
        BaseClass.__init__( self, name, age )
        self.height = height
    
    def speech( self ):
        BaseClass.talk( self )
        print "sub Class", self.name, self.age, self.height
        









if __name__ == '__main__':
    subclass_obj = SubClass( "xhj", "23", "1.75cm" )
    subclass_obj.talk()
    subclass_obj.speech()
    pass
