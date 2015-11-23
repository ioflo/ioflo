"""arbiting.py arbiter deed module

"""
#print("module {0}".format(__name__))

import time
import struct
from collections import deque
import inspect

from ..aid.sixing import *
from ..aid.odicting import odict

from . import doing

from ..aid.consoling import getConsole
console = getConsole()


#Arbiter Class
class Arbiter(doing.Doer):
    """Arbiter Doer Class
       Generic Arbiter Class for Arbiters should be subclassed

    """
    def __init__(self, output, group, inputs, **kw):
        """Initialize Instance

           Arbiters use three types of inputs to do the arbitration:
              selections must evaluate to boolean True of False but using Python rules so
                 could be any type rule is
                    if sel: then the input is selected
                    otherwise input is ignored
              confidences are used either for threshold or for weighting output
                 confidences can be number in interval [ 0.0, 1.0] or Boolean or None.
                 when necessary arbiter will convert confidence to be in [0.0, 1.0] using rules
                    if None then assumed = 1.0,
                    if True then 1.0
                    if False then 0.0
                    otherwise hard limit and convert numbers to interval [0.0, 1.0]
              importances are assumed to be in interval [0.0, 1.0] but will still work properly
                 if non negative numbers

              Values are not constrained for Switch and Priority arbiters but must be numbers for
                 Weighted arbiter.
                 With a weighted arbiter if one of the input values is not number then
                    the weighted arbiter uses the default outputs.

           Init Parameters:

           output is path name of share for output/truth of arbiter

           group is path name of group in store, group has following subgroups or shares:
              group.default = share of default value and confidence (truth) for arbiter
              group.inimps = data structure of input importances
              group.insels = data structure of input selections


           inputs is ordered dictionary (odict) of inputs:
              key = selection tag name for input
              value = tuple of input data
                 (share path name, selection importance)
                    tag is user friendly short name for input used to change selection or importance

           instance attributes
           .output = reference to output share
           .group = copy of group path name
           .default = reference to group.default value and conf share
           .insels = reference to group.insels share
           .inimps = reference to group.inimps share
           .inputs = ordered dictionary (odict) of tags and input shares

           inherited instance attributes:
           .name
           .store

        """
        super(Arbiter,self).__init__(**kw)

        #create it if it does not already exist
        self.output = self.store.create(output).create(value = 0.0)
        #updateJointly
        self.output.value = 0.0 #force value
        self.output.truth = 0.0 #force truth
        self.group = group

        #create default value conf and assign defaults if not already assigned
        self.default = self.store.create(group + '.default').create(value = 0.0)

        #check to make sure default truth in [0.0, 1.0]
        if not self.GoodTruth(self.default.truth):
            self.default.truth = self.FixTruth(self.default.truth)

        #create insels and inimps if not exist
        self.insels = self.store.create(group + '.insels')
        self.inimps = self.store.create(group + '.inimps')

        #initialize inputs, inimps and insels
        self.inputs = odict()

        for tag, stuff in inputs.items():
            input, sel, imp = stuff #break out tuple inputpath, selection, importance
            if tag: #filter out '' tags, not allowed
                input = self.store.create(input) #create share reference from path name
                self.inputs[tag] = input #save it
                self.insels.create(**{tag : sel}) #initialize selection if not exist
                self.inimps.create(**{tag : imp}) #initialize importance if not exist


    def _expose(self):
        """prints out arbiter parameters

        """
        msg = "Arbiter %s\n" % self.name
        msg += "   group = %s  outval = %s outcnf = %s defval = %s defcnf = %s\n" %\
              (self.group, self.output.value, self.output.truth, self.default.value, self.default.truth)
        msg += "   inputs = \n"
        for tag, input in self.inputs.items():
            msg += "      tag = %s, input = %s, sel = %s, imp = %s,\n" %\
                  (tag, input.name, self.insels.fetch(tag), self.inimps.fetch(tag))
            msg += "      input value = %s input truth = %s\n" % (input.value, input.truth)
        console.terse(msg)

    def update(self):
        """update should be overridden by subclass

        """
        pass


    def action(self, **kw):
        """action is to update arbiter

        """
        console.profuse("Updating arbiter {0}\n".format(self.name))
        self.update()


    @staticmethod
    def GoodTruth(truth):
        """Check if truth float in range [0.0, 1.0]
           this so only FixTruth when needed for initing default confidence
        """
        if isinstance(truth, float) and (truth >= 0.0) and (truth <= 1.0):
            return True

        return False

    @staticmethod
    def FixTruth(truth):
        """make truth to be float in range [0.0, 1.0]
           if truth is None or Boolean True then make 1.0
           If truth is Boolean False then make 0.0
           otherwise Truth assumed to be number so hard limit to interval [0.0, 1.0]
        """
        if truth is None or truth is True: #None or Boolean True
            truth = 1.0
        elif truth is False: #Boolean False
            truth = 0.0
        else:
            truth = float(min(1.0,max(0.0,truth)))

        return truth

#Switch Arbiter Class
class ArbiterSwitch(Arbiter):
    """ArbiterSwitch Arbiter Deed Class


    """
    def update(self,stamp = None):
        """update switch arbiter algorithm
           simply switch selected input to output
           ignore importances
           ignore threshold on confidence

           find first input whose:
              selection is logically True
              if found then output's value/truth is found input's value/truth

           otherwise output's value/truth is default's value/truth

        """
        for tag, input in self.inputs.items():
            if self.insels.fetch(tag): #first one that is selected
                #self.output.updateJointly(value = input.value, truth = input.truth, stamp = stamp)
                self.output.value = input.value
                self.output.truth = input.truth
                self.output.stamp = stamp
                return

        #self.output.updateJointly(value = self.default.value,
        #                           truth = self.default.truth, stamp = stamp)
        self.output.value = self.default.value
        self.output.truth = self.default.truth
        self.output.stamp = stamp

#Priority Arbiter Class
class ArbiterPriority(Arbiter):
    """ArbiterPriority Arbiter Deed Class


    """
    def update(self,stamp = None):
        """update priority arbiter algorithm

           an input is selected if its selection is logically true
           an input is sufficient if its confidence is > default truth
           confidence constrained to range [0.0, 1.0]
           if an input's truth is True or None then use truth = 1.0
           an input is most important if it has maximum importance of all selected sufficient inputs

           find first and most important input

           if found then output's value/truth is found input's value/truth
           else output's value/truth is default's value/truth

        """
        #find max selected input
        inputmax = None
        impmax = 0.0
        truthmax = 0.0
        for tag, input in self.inputs.items():
            truth = self.FixTruth(input.truth) #fix truth to be float in range [0.0, 1.0]
            imp = self.inimps.fetch(tag)  # or could use form self.inimps[tag]
            if (  self.insels.fetch(tag) and
                  (truth > self.default.truth) and
                  (imp > impmax) ):
                inputmax = input
                impmax = imp
                truthmax = truth

        if inputmax:
            #self.output.updateJointly(value = inputmax.value, truth = truthmax, stamp = stamp)
            self.output.value = inputmax.value
            self.output.truth = truthmax
            self.output.stamp = stamp
        else:
            #self.output.updateJointly(value = self.default.value,
            #                              truth = self.default.truth, stamp = stamp)
            self.output.value = self.default.value
            self.output.truth = self.default.truth
            self.output.stamp = stamp

#Trusted Arbiter Class
class ArbiterTrusted(Arbiter):
    """ArbiterTrusted Arbiter Deed Class


    """
    def update(self,stamp = None):
        """update trusted arbiter algorithm

           an input is selected if its selection is logically true
           an input is sufficient if its confidence is > default truth
           input's truth confidence constrained to range [0.0, 1.0]
           if an input's truth is True or None then use truth = 1.0
           an input has the highest confidence if its confidence is maximum amoung all
              selected sufficient inputs
           an input is most important if it has maximum importance of all highest confidence inputs

           find first most important input

           if found then output's value/truth is found input's value/truth
           else output's value/truth is default's value/truth

        """
        #find max selected input
        inputmax = None
        impmax = 0.0
        truthmax = 0.0
        for tag, input in self.inputs.items():
            sel = self.insels.fetch(tag) #or could use form self.insel[tag]
            truth = self.FixTruth(input.truth) #fix truth to be float in range [0.0, 1.0]
            imp = self.inimps.fetch(tag)
            if (sel and (truth > self.default.truth) ):
                if (truth > truthmax):
                    truthmax = truth
                    impmax = imp
                    inputmax = input
                elif ( (truth == truthmax) and (imp > imputmax) ):
                    truthmax = truth
                    impmax = imp
                    inputmax = input

        if inputmax:
            #self.output.updateJointly(value = inputmax.value, truth = truthmax, stamp = stamp)
            self.output.value = inputmax.value
            self.output.truth = truthmax
            self.output.stamp = stamp
        else:
            #self.output.updateJointly(value = self.default.value,
            #                           truth = self.default.truth, stamp = stamp)
            self.output.value = self.default.value
            self.output.truth = self.default.truth
            self.output.stamp = stamp

#Weighted Arbiter Class
class ArbiterWeighted(Arbiter):
    """ArbiterWeighted Arbiter Deed Class


    """
    def update(self,stamp = None):
        """update weighted arbiter algorithm

           an input is selected if its selection is logically true
           compute normalized weighted average of all selected inputs where average is given by
           weighted conf = Sum(imp * cnf)/Sum(imp)
           weighted value = Sum(imp * cnf * value)/Sum(imp * cnf)

           input truth values are fixed up to be float in range [0.0, 1.0]

           if weighted conf > default truth then
              output's value/truth is found input's value/fixed truth
           else
              output's value/truth is default's value/truth

        """
        wgtval = 0.0
        wgtcnf = 0.0
        wgtimp = 0.0
        try:
            for tag, input in self.inputs.items():
                if self.insels.fetch(tag): #or could use form self.insel[tag]
                    truth = self.FixTruth(input.truth)
                    imp = self.inimps.fetch(tag) #or could use form self.insel[tag]
                    wgtimp += imp
                    wgtcnf += imp * truth
                    wgtval += imp * truth * input.value

            wgtval = wgtval / float(wgtcnf)
            wgtcnf = wgtcnf / float(wgtimp)

        except TypeError:#one of the input values is not number
            console.terse("     Warning, bad input value for Arbiter {0}\n".format(self.name))
            #self.output.updateJointly(value = self.default.value,
            #                              truth = self.default.truth, stamp = stamp)
            self.output.value = self.default.value
            self.output.truth = self.default.truth
            self.output.stamp = stamp
            return
        except ZeroDivisionError:  #no selected input with non zero truth or importance
            #self.output.updateJointly(value = self.default.value,
            #                           truth = self.default.truth, stamp = stamp)
            self.output.value = self.default.value
            self.output.truth = self.default.truth
            self.output.stamp = stamp
            return


        if wgtcnf > self.default.truth:
            #self.output.updateJointly(value = wgtval, truth = wgtcnf, stamp = stamp)
            self.output.value = wgtval
            self.output.truth = wgtcnf
            self.output.stamp = stamp

        else:
            #self.output.updateJointly(value = self.default.value,
            #                           truth = self.default.truth, stamp = stamp)
            self.output.value = self.default.value
            self.output.truth = self.default.truth
            self.output.stamp = stamp

