# -*- coding: utf-8 -*-
"""
Unit Test Template
"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import time

from ioflo.aid.sixing import *
from ioflo.aid import odict
from ioflo.test import testing
from ioflo.base import globaling
from ioflo.base import Data, Deck

from ioflo.aid.consoling import getConsole

from ioflo.base import storing
from ioflo.base import logging

console = getConsole()


def setUpModule():
    console.reinit(verbosity=console.Wordage.profuse)

def tearDownModule():
    console.reinit(verbosity=console.Wordage.concise)


class LoggerTestCase(testing.LoggerIofloTestCase):
    """
    Example TestCase
    """

    def setUp(self):
        """
        Call super if override so House Framer and Frame are setup correctly
        """
        super(LoggerTestCase, self).setUp()

    def tearDown(self):
        """
        Call super if override so House Framer and Frame are torn down correctly
        """
        super(LoggerTestCase, self).tearDown()


    def testLogger(self):
        """
        Test creating a logger with a log and loggees
        """
        console.terse("{0}\n".format(self.testLogger.__doc__))
        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        heading = self.store.create('pose.heading').create(value = 0.0)
        position = self.store.create('pose.position').create([("north", 10.0), ("east", 5.0)])

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFilename='',
                          rule=globaling.ALWAYS)

        self.assertEqual(log.baseFilename, log.name)
        self.assertEqual(log.path, '')
        self.assertEqual(log.file, None)
        self.assertEqual(log.kind, 'text')

        self.assertEqual(log.rule, globaling.ALWAYS)
        self.assertEqual(log.action, log.always)

        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        log.addLoggee(tag = 'pos', loggee = 'pose.position')
        log.resolve()

        self.logger.addLog(log)
        self.logger.reopen()  # this updates paths on all logs
        self.assertTrue(self.logger.path.startswith('/tmp/log/ioflo/HouseTest/LoggerTest_'))
        self.assertTrue(log.path.startswith(self.logger.path))
        self.assertTrue(log.path.endswith(log.baseFilename + '.txt'))
        self.assertTrue(log.file)

        log.prepare()
        self.assertEqual(log.formats, {'_time': '%s',
                                        'heading': odict([('value', '\t%s')]),
                                        'pos': odict([('north', '\t%s'), ('east', '\t%s')])})
        #self.assertEqual(log.formats, {'_time': '%0.4f',
                                        #'heading': odict([('value', '\t%0.4f')]),
                                        #'pos': odict([('north', '\t%0.4f'), ('east', '\t%0.4f')])})

        self.house.store.changeStamp(0.0)

        log() #log
        for i in range(20):
            self.store.advanceStamp(0.125)
            if i == 5:
                heading.value += 0.0
                position.data.north += 0.0
                position.data.east -= 0.0
            elif i == 10:
                pass
            else:
                heading.value = float(i)
                position.data.north += 2.0
                position.data.east -= 1.5

            log() #log

        log.flush()
        log.file.seek(0)
        line = log.file.readline()
        self.assertEqual(line, 'text\tAlways\ttest\n')
        line = log.file.readline()
        self.assertEqual(line, '_time\theading\tpos.north\tpos.east\n')
        lines = log.file.readlines()
        self.assertEqual(lines, ['0.0\t0.0\t10.0\t5.0\n',
                                '0.125\t0.0\t12.0\t3.5\n',
                                '0.25\t1.0\t14.0\t2.0\n',
                                '0.375\t2.0\t16.0\t0.5\n',
                                '0.5\t3.0\t18.0\t-1.0\n',
                                '0.625\t4.0\t20.0\t-2.5\n',
                                '0.75\t4.0\t20.0\t-2.5\n',
                                '0.875\t6.0\t22.0\t-4.0\n',
                                '1.0\t7.0\t24.0\t-5.5\n',
                                '1.125\t8.0\t26.0\t-7.0\n',
                                '1.25\t9.0\t28.0\t-8.5\n',
                                '1.375\t9.0\t28.0\t-8.5\n',
                                '1.5\t11.0\t30.0\t-10.0\n',
                                '1.625\t12.0\t32.0\t-11.5\n',
                                '1.75\t13.0\t34.0\t-13.0\n',
                                '1.875\t14.0\t36.0\t-14.5\n',
                                '2.0\t15.0\t38.0\t-16.0\n',
                                '2.125\t16.0\t40.0\t-17.5\n',
                                '2.25\t17.0\t42.0\t-19.0\n',
                                '2.375\t18.0\t44.0\t-20.5\n',
                                '2.5\t19.0\t46.0\t-22.0\n'])

        log.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass



    def testLogAlways(self):
        """
        Test creating a logger with a log and loggees
        """
        console.terse("{0}\n".format(self.testLogAlways.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        heading = self.store.create('pose.heading').create(value = 0.0)
        position = self.store.create('pose.position').create([("north", 10.0), ("east", 5.0)])

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.ALWAYS)

        self.assertEqual(log.baseFilename, log.name)
        self.assertEqual(log.path, '')
        self.assertEqual(log.file, None)
        self.assertEqual(log.kind, 'text')

        self.assertEqual(log.rule, globaling.ALWAYS)
        self.assertEqual(log.action, log.always)

        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        log.addLoggee(tag = 'pos', loggee = 'pose.position')

        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well


        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertTrue(self.logger.path.startswith('/tmp/log/ioflo/HouseTest/LoggerTest_'))
        self.assertTrue(log.path.startswith(self.logger.path))
        self.assertTrue(log.path.endswith(log.baseFilename + '.txt'))
        self.assertTrue(log.file)
        self.assertEqual(log.formats, {'_time': '%s',
                                        'heading': odict([('value', '\t%s')]),
                                        'pos': odict([('north', '\t%s'), ('east', '\t%s')])})

        #self.assertEqual(log.formats, {'_time': '%0.4f',
                                        #'heading': odict([('value', '\t%0.4f')]),
                                        #'pos': odict([('north', '\t%0.4f'), ('east', '\t%0.4f')])})

        for i in range(20):
            self.store.advanceStamp(0.125)
            if i == 5:
                heading.value += 0.0
                position.data.north += 0.0
                position.data.east -= 0.0
            elif i == 10:
                pass
            else:
                heading.value = float(i)
                position.data.north += 2.0
                position.data.east -= 1.5

            status = self.logger.runner.send(globaling.RUN)

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # logs once and closes logs

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        line = log.file.readline()
        self.assertEqual(line, 'text\tAlways\ttest\n')
        line = log.file.readline()
        self.assertEqual(line, '_time\theading\tpos.north\tpos.east\n')
        lines = log.file.readlines()
        self.assertEqual(lines, ['0.0\t0.0\t10.0\t5.0\n',
                                    '0.125\t0.0\t12.0\t3.5\n',
                                    '0.25\t1.0\t14.0\t2.0\n',
                                    '0.375\t2.0\t16.0\t0.5\n',
                                    '0.5\t3.0\t18.0\t-1.0\n',
                                    '0.625\t4.0\t20.0\t-2.5\n',
                                    '0.75\t4.0\t20.0\t-2.5\n',
                                    '0.875\t6.0\t22.0\t-4.0\n',
                                    '1.0\t7.0\t24.0\t-5.5\n',
                                    '1.125\t8.0\t26.0\t-7.0\n',
                                    '1.25\t9.0\t28.0\t-8.5\n',
                                    '1.375\t9.0\t28.0\t-8.5\n',
                                    '1.5\t11.0\t30.0\t-10.0\n',
                                    '1.625\t12.0\t32.0\t-11.5\n',
                                    '1.75\t13.0\t34.0\t-13.0\n',
                                    '1.875\t14.0\t36.0\t-14.5\n',
                                    '2.0\t15.0\t38.0\t-16.0\n',
                                    '2.125\t16.0\t40.0\t-17.5\n',
                                    '2.25\t17.0\t42.0\t-19.0\n',
                                    '2.375\t18.0\t44.0\t-20.5\n',
                                    '2.5\t19.0\t46.0\t-22.0\n',
                                    '2.625\t19.0\t46.0\t-22.0\n'])

        self.assertIsNot(log.stamp, None)
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.START)  # logs once no headers since log stamp not none
        self.store.advanceStamp(0.125)
        heading.value += 5.0
        status = self.logger.runner.send(globaling.RUN)  # logs once
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # logs once and closes logs

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                '_time\theading\tpos.north\tpos.east\n',
                                '0.0\t0.0\t10.0\t5.0\n',
                                '0.125\t0.0\t12.0\t3.5\n',
                                '0.25\t1.0\t14.0\t2.0\n',
                                '0.375\t2.0\t16.0\t0.5\n',
                                '0.5\t3.0\t18.0\t-1.0\n',
                                '0.625\t4.0\t20.0\t-2.5\n',
                                '0.75\t4.0\t20.0\t-2.5\n',
                                '0.875\t6.0\t22.0\t-4.0\n',
                                '1.0\t7.0\t24.0\t-5.5\n',
                                '1.125\t8.0\t26.0\t-7.0\n',
                                '1.25\t9.0\t28.0\t-8.5\n',
                                '1.375\t9.0\t28.0\t-8.5\n',
                                '1.5\t11.0\t30.0\t-10.0\n',
                                '1.625\t12.0\t32.0\t-11.5\n',
                                '1.75\t13.0\t34.0\t-13.0\n',
                                '1.875\t14.0\t36.0\t-14.5\n',
                                '2.0\t15.0\t38.0\t-16.0\n',
                                '2.125\t16.0\t40.0\t-17.5\n',
                                '2.25\t17.0\t42.0\t-19.0\n',
                                '2.375\t18.0\t44.0\t-20.5\n',
                                '2.5\t19.0\t46.0\t-22.0\n',
                                '2.625\t19.0\t46.0\t-22.0\n',
                                '2.75\t19.0\t46.0\t-22.0\n',
                                '2.875\t24.0\t46.0\t-22.0\n',
                                '3.0\t24.0\t46.0\t-22.0\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


    def testLogOnce(self):
        """
        Test log with once rule
        """
        console.terse("{0}\n".format(self.testLogOnce.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.ONCE)

        self.assertEqual(log.rule, globaling.ONCE)
        self.assertEqual(log.action, log.once)

        heading = self.store.create('pose.heading').create(value = 0.0)
        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, odict([('_time', '%s'), ('heading', odict([('value', '\t%s')]))]))

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        heading.value += 0.0  # updated but same value
        status = self.logger.runner.send(globaling.RUN)  # logs since updated
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        heading.value += 5.0  # update with different value
        status = self.logger.runner.send(globaling.RUN)  # logs since updated
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not updated

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tOnce\ttest\n', '_time\theading\n', '0.0\t0.0\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


    def testLogNever(self):
        """
        Test log with never rule
        """
        console.terse("{0}\n".format(self.testLogNever.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.NEVER)

        self.assertEqual(log.rule, globaling.NEVER)
        self.assertEqual(log.action, log.never)

        heading = self.store.create('pose.heading').create(value = 0.0)
        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, odict([('_time', '%s'), ('heading', odict([('value', '\t%s')]))]))

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        heading.value += 0.0  # updated but same value
        status = self.logger.runner.send(globaling.RUN)  # logs since updated
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        heading.value += 5.0  # update with different value
        status = self.logger.runner.send(globaling.RUN)  # logs since updated
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not updated

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tNever\ttest\n', '_time\theading\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass



    def testLogUpdate(self):
        """
        Test log with update rule
        """
        console.terse("{0}\n".format(self.testLogUpdate.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.UPDATE)

        self.assertEqual(log.rule, globaling.UPDATE)
        self.assertEqual(log.action, log.update)

        heading = self.store.create('pose.heading').create(value = 0.0)
        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, odict([('_time', '%s'), ('heading', odict([('value', '\t%s')]))]))

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        heading.value += 0.0  # updated but same value
        status = self.logger.runner.send(globaling.RUN)  # logs since updated
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        heading.value += 5.0  # update with different value
        status = self.logger.runner.send(globaling.RUN)  # logs since updated
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not updated

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tUpdate\ttest\n',
                                '_time\theading\n',
                                '0.0\t0.0\n',
                                '0.25\t0.0\n',
                                '0.5\t5.0\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass



    def testLogUpdateFields(self):
        """
        Test log with update rule and passed in fields list
        """
        console.terse("{0}\n".format(self.testLogUpdateFields.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.UPDATE)

        self.assertEqual(log.rule, globaling.UPDATE)
        self.assertEqual(log.action, log.update)

        ned = self.store.create('pose.ned').create(north = 0.0, east=0.0, down=0.0)
        log.addLoggee(tag = 'ned', loggee = 'pose.ned', fields=['north', 'east'])
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, {'_time': '%s',
                                        'ned': odict([('north', '\t%s'), ('east', '\t%s')])}
                                       )

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        ned.update(north=0.0)  # updated but same value
        status = self.logger.runner.send(globaling.RUN)  # log since updated
        self.store.advanceStamp(0.125)
        ned.update(down=0.0)  # updated a field but not loggee field
        status = self.logger.runner.send(globaling.RUN)  # log since updated any field
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        ned.update(north=5.0, east=7.0)  # update with different values
        status = self.logger.runner.send(globaling.RUN)  # log since updated
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not updated

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tUpdate\ttest\n',
                                '_time\tned.north\tned.east\n',
                                '0.0\t0.0\t0.0\n',
                                '0.25\t0.0\t0.0\n',
                                '0.375\t0.0\t0.0\n',
                                '0.5\t5.0\t7.0\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


    def testLogChange(self):
        """
        Test log with change rule
        """
        console.terse("{0}\n".format(self.testLogChange.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.CHANGE)

        self.assertEqual(log.rule, globaling.CHANGE)
        self.assertEqual(log.action, log.change)

        heading = self.store.create('pose.heading').create(value = 0.0)
        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, odict([('_time', '%s'), ('heading', odict([('value', '\t%s')]))]))
        self.assertTrue('heading' in log.lasts)

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        heading.value += 0.0  # updated but same value
        status = self.logger.runner.send(globaling.RUN)  # no log since updated but not changed
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        heading.value += 5.0  # update with different value
        status = self.logger.runner.send(globaling.RUN)  # logs since changed
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not updated

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tChange\ttest\n', '_time\theading\n', '0.0\t0.0\n', '0.5\t5.0\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


    def testLogChangeFields(self):
        """
        Test log with update rule and passed in fields list
        """
        console.terse("{0}\n".format(self.testLogChangeFields.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.CHANGE)

        self.assertEqual(log.rule, globaling.CHANGE)
        self.assertEqual(log.action, log.change)

        ned = self.store.create('pose.ned').create(north = 0.0, east=0.0, down=0.0)
        fields = ['north', 'east']
        log.addLoggee(tag = 'ned', loggee = 'pose.ned', fields=fields)
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, {'_time': '%s',
                                    'ned': odict([('north', '\t%s'), ('east', '\t%s')])})
        self.assertTrue('ned' in log.lasts)
        last = log.lasts['ned']
        for field in fields:
            self.assertEqual(getattr(last, field), 0.0)

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        ned.update(north=0.0)  # updated but same value
        status = self.logger.runner.send(globaling.RUN)  # not log since not changed
        self.store.advanceStamp(0.125)
        ned.update(down=4.0)  # updated a field but not loggee field
        status = self.logger.runner.send(globaling.RUN)  # not log since not changed given field
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        ned.update(north=5.0, east=7.0)  # update with different values
        status = self.logger.runner.send(globaling.RUN)  # log since changed given field
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not changed

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tChange\ttest\n',
                                '_time\tned.north\tned.east\n',
                                '0.0\t0.0\t0.0\n',
                                '0.5\t5.0\t7.0\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


    def testLogStreak(self):
        """
        Test log with streak rule
        """
        console.terse("{0}\n".format(self.testLogStreak.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.STREAK)

        self.assertEqual(log.rule, globaling.STREAK)
        self.assertEqual(log.action, log.streak)

        heading = self.store.create('pose.heading').create(value = 0.0)
        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, odict([('_time', '%s'), ('heading', odict([('value', '\t%s')]))]))

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        heading.value += 0.0  # updated but same value
        status = self.logger.runner.send(globaling.RUN)  # no log since updated but not changed
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        heading.value += 5.0  # update with different value
        status = self.logger.runner.send(globaling.RUN)  # logs since changed
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not updated

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tStreak\ttest\n',
                                '_time\theading\n',
                                '0.0\t0.0\n',
                                '0.125\t0.0\n',
                                '0.25\t0.0\n',
                                '0.375\t0.0\n',
                                '0.5\t5.0\n',
                                '0.625\t5.0\n'])
        log.file.close()

        heading.value = ["hello", "how", "are", "you", 5.0, 6, 7]

        self.assertEqual(log.stamp, 0.625)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, odict([('_time', '%s'), ('heading', odict([('value', '\t%s')]))]))
        #self.assertTrue('heading' in log.lasts)

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        heading.value.append(10.0)
        status = self.logger.runner.send(globaling.RUN)  # no log since updated but not changed
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        heading.value.append(15)
        heading.value.append(20)
        status = self.logger.runner.send(globaling.RUN)  # logs since changed
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not updated

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tStreak\ttest\n',
                                '_time\theading\n',
                                '0.0\t0.0\n',
                                '0.125\t0.0\n',
                                '0.25\t0.0\n',
                                '0.375\t0.0\n',
                                '0.5\t5.0\n',
                                '0.625\t5.0\n',
                                '0.625\thello\n',
                                '0.625\thow\n',
                                '0.625\tare\n',
                                '0.625\tyou\n',
                                '0.625\t5.0\n',
                                '0.625\t6\n',
                                '0.625\t7\n',
                                '0.875\t10.0\n',
                                '1.125\t15\n',
                                '1.125\t20\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


    def testLogStreakFields(self):
        """
        Test log with streak rule and fields
        """
        console.terse("{0}\n".format(self.testLogStreakFields.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.STREAK)

        self.assertEqual(log.rule, globaling.STREAK)
        self.assertEqual(log.action, log.streak)

        stuff = self.store.create('big.stuff').create([('sack', []),
                                                   ('bag', [])])
        fields = ['bag', 'dummy']  # reorder to second field gets logged
        log.addLoggee(tag = 'puff', loggee = 'big.stuff', fields=fields)
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, odict([('_time', '%s'), ('puff', odict([('bag', '\t%s')]))]))

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since empty
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        stuff.data.bag.extend(["Rain", "Falls"])
        stuff.data.sack.extend(["Sun", "Shines"])
        status = self.logger.runner.send(globaling.RUN)  # log since not empty
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since empty
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        stuff.data.bag.extend(["Sky", "Blue", "Tree", "Green"])
        status = self.logger.runner.send(globaling.RUN)  # logs since not empty
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not updated

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tStreak\ttest\n',
                                '_time\tpuff\n',
                                '0.25\tRain\n',
                                '0.25\tFalls\n',
                                '0.5\tSky\n',
                                '0.5\tBlue\n',
                                '0.5\tTree\n',
                                '0.5\tGreen\n'])
        log.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


    def testLogDeck(self):
        """
        Test log with deck rule
        """
        console.terse("{0}\n".format(self.testLogDeck.__doc__))

        self.assertEqual(self.house.store, self.store)
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(self.logger.runner)  # runner generator is made when logger created

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.DECK)

        self.assertEqual(log.rule, globaling.DECK)
        self.assertEqual(log.action, log.deck)

        ned = self.store.create('pose.ned')
        fields = ['north', 'east']
        log.addLoggee(tag = 'ned', loggee = 'pose.ned', fields=fields)
        self.logger.addLog(log)
        self.logger.resolve()  # resolves logs as well

        ned.push(odict(north=0.0, east=0.0, down=0.0))
        ned.push(odict(north=5.0, east=4.0, down=3.0))
        ned.push(odict(north=6.0, east=3.0, down=2.0))
        ned.push(odict(east=2.0, down=1.0))
        ned.push(odict(down=0.0))
        ned.push(odict(north=7.0, east=4.0, down=3.0))
        ned.push(["hi", "there"])
        ned.push(odict(north=8.0, east=5.0, down=4.0))

        self.assertEqual(ned.deck, Deck([odict([('down', 0.0),('north', 0.0), ('east', 0.0)]),
                                         odict([('down', 3.0), ('north', 5.0), ('east', 4.0)]),
                                         odict([('down', 2.0), ('north', 6.0), ('east', 3.0)]),
                                         odict([('down', 1.0), ('east', 2.0)]),
                                         odict([('down', 0.0)]),
                                         odict([('down', 3.0), ('north', 7.0), ('east', 4.0)]),
                                         ['hi', 'there'],
                                         odict([('down', 4.0), ('north', 8.0), ('east', 5.0)])]))

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)
        status = self.logger.runner.send(globaling.START)  # reopens prepares and logs once
        self.assertEqual(log.formats, {'_time': '%s',
                                       'ned': odict([('north', '\t%s'), ('east', '\t%s')])})

        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # no log since not updated
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.25)
        ned.push(odict(north=9.0, east=6.0, down=5.0))  # push another
        status = self.logger.runner.send(globaling.RUN)  # not log since not changed
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.RUN)  # not log since not changed given field
        self.store.advanceStamp(0.125)
        self.assertEqual(self.store.stamp, 0.5)
        ned.push(odict(north=10.0, east=7.0, down=6.0))  # push
        status = self.logger.runner.send(globaling.RUN)  # log since changed given field
        self.store.advanceStamp(0.125)
        status = self.logger.runner.send(globaling.STOP)  # not log since not changed

        log.reopen()
        log.file.seek(0)  # reopen appends so seek back to start
        lines = log.file.readlines()
        self.assertEqual(lines, ['text\tDeck\ttest\n',
                                '_time\tned.north\tned.east\n',
                                '0.0\t0.0\t0.0\n',
                                '0.0\t5.0\t4.0\n',
                                '0.0\t6.0\t3.0\n',
                                '0.0\t\t2.0\n',
                                '0.0\t\t\n',
                                '0.0\t7.0\t4.0\n',
                                '0.0\t8.0\t5.0\n',
                                '0.25\t9.0\t6.0\n',
                                '0.5\t10.0\t7.0\n'])
        log.file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


class HouseTestCase(testing.HouseIofloTestCase):
    """
    Example TestCase
    """

    def setUp(self):
        """
        Call super if override so House Framer and Frame are setup correctly
        """
        super(HouseTestCase, self).setUp()

    def tearDown(self):
        """
        Call super if override so House Framer and Frame are torn down correctly
        """
        super(HouseTestCase, self).tearDown()


    def testSetup(self):
        """
        Test creating setting up a logger
        """
        console.terse("{0}\n".format(self.testSetup.__doc__))
        self.assertEqual(self.house.store, self.store)

        prefix = "/tmp/log/ioflo"
        flush = 2.0
        cycle = 0.0
        keep =  0
        logger = logging.Logger(name="LoggerTest",
                                store=self.store,
                                schedule=globaling.ACTIVE,
                                prefix=prefix,
                                flushPeriod=flush,
                                cycle=cycle,
                                keep=keep)

        self.assertEqual(logger.flushPeriod, flush)
        self.assertEqual(logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(logger.runner)  # runner generator is made when logger created
        self.assertEqual(logger.cyclePeriod, cycle)
        self.assertEqual(logger.keep, keep)
        self.assertEqual(logger.flushStamp, 0.0)
        self.assertEqual(logger.path, '')

        self.assertEqual(logger.logs, [])

        self.house.taskers.append(logger)
        self.house.mids.append(logger)
        self.house.orderTaskables()

        self.house.store.changeStamp(0.0)
        self.assertEqual(logger.stamp, 0.0)

        status = logger.runner.send(globaling.START)  # reopens prepares
        self.assertTrue(logger.path.startswith("/tmp/log/ioflo/HouseTest/LoggerTest_"))


    def testCycle(self):
        """
        Test creating setting up a logger with log to rotate
        """
        console.terse("{0}\n".format(self.testCycle.__doc__))
        self.assertEqual(self.house.store, self.store)

        prefix = "/tmp/log/ioflo"
        flush = 3.0
        cyclePeriod = 0.5
        keep =  2
        fileSize = 10
        logger = logging.Logger(name="LoggerTest",
                                store=self.store,
                                schedule=globaling.ACTIVE,
                                prefix=prefix,
                                flushPeriod=flush,
                                keep=keep,
                                cyclePeriod=cyclePeriod,
                                fileSize=fileSize)

        self.assertEqual(logger.flushPeriod, flush)
        self.assertEqual(logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(logger.runner)  # runner generator is made when logger created
        self.assertEqual(logger.cyclePeriod, cyclePeriod)
        self.assertEqual(logger.keep, keep)
        self.assertEqual(logger.fileSize, fileSize)
        self.assertEqual(logger.cycleStamp, 0.0)
        self.assertEqual(logger.flushStamp, 0.0)
        self.assertEqual(logger.path, '')

        self.assertEqual(logger.logs, [])

        self.house.taskers.append(logger)
        self.house.mids.append(logger)
        self.house.orderTaskables()

        self.house.store.changeStamp(0.0)
        self.assertEqual(logger.stamp, 0.0)

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.ALWAYS)

        self.assertEqual(log.baseFilename, log.name)
        self.assertEqual(log.path, '')
        self.assertEqual(log.file, None)
        self.assertEqual(log.kind, 'text')

        self.assertEqual(log.rule, globaling.ALWAYS)
        self.assertEqual(log.action, log.always)

        logger.addLog(log)

        heading = self.store.create('pose.heading').create(value = 0.0)
        #position = self.store.create('pose.position').create([("north", 10.0), ("east", 5.0)])

        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        #log.addLoggee(tag = 'pos', loggee = 'pose.position')

        logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)

        status = logger.runner.send(globaling.START)  # reopens prepares and logs once

        self.assertTrue(logger.path.startswith('/tmp/log/ioflo/HouseTest/LoggerTest_'))
        self.assertTrue(log.path.startswith(logger.path))
        self.assertTrue(log.path.endswith(log.baseFilename + '.txt'))
        self.assertTrue(log.file)

        self.assertEqual(len(log.paths), keep+1)
        for k, path in enumerate(log.paths[1:]):
            self.assertTrue(path.startswith(logger.path))
            base = os.path.basename(path)
            root, ext = os.path.splitext(base)
            self.assertTrue(root.endswith("{0:02}".format(k+1)))

        for i in range(16):
            self.store.advanceStamp(0.125)
            heading.value += 1.0
            status = logger.runner.send(globaling.RUN)

        self.store.advanceStamp(0.125)
        heading.value += 1.0
        status = logger.runner.send(globaling.STOP)  # logs once and closes logs

        path0, path1, path2 = log.paths

        file0 = open(path0, "r")
        lines = file0.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n', '_time\theading\n',
                                 '2.125\t17.0\n'])
        file0.close()

        file1 = open(path1, "r")
        lines = file1.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                '_time\theading\n',
                                '1.625\t13.0\n',
                                '1.75\t14.0\n',
                                '1.875\t15.0\n',
                                '2.0\t16.0\n'])
        file1.close()

        file2 = open(path2, "r")
        lines = file2.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                '_time\theading\n',
                                '1.125\t9.0\n',
                                '1.25\t10.0\n',
                                '1.375\t11.0\n',
                                '1.5\t12.0\n'])
        file2.close()

        for path in log.paths:  # remove files to clean up
            try:
                os.remove(path)
            except OSError as ex:
                pass


    def testCycleReuse(self):
        """
        Test logger with rotate and non unique directory name
        """
        console.terse("{0}\n".format(self.testCycleReuse.__doc__))
        self.assertEqual(self.house.store, self.store)

        prefix = "/tmp/log/ioflo"
        flush = 3.0
        cyclePeriod = 0.5
        keep =  2
        fileSize = 50
        logger = logging.Logger(name="LoggerTest",
                                store=self.store,
                                schedule=globaling.ACTIVE,
                                prefix=prefix,
                                flushPeriod=flush,
                                keep=keep,
                                cyclePeriod=cyclePeriod,
                                fileSize=fileSize,
                                reuse=True)

        self.assertEqual(logger.flushPeriod, flush)
        self.assertEqual(logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(logger.runner)  # runner generator is made when logger created
        self.assertEqual(logger.cyclePeriod, cyclePeriod)
        self.assertEqual(logger.keep, keep)
        self.assertEqual(logger.fileSize, fileSize)
        self.assertEqual(logger.cycleStamp, 0.0)
        self.assertEqual(logger.flushStamp, 0.0)
        self.assertEqual(logger.path, '')
        self.assertTrue(logger.reuse)

        self.assertEqual(logger.logs, [])

        self.house.taskers.append(logger)
        self.house.mids.append(logger)
        self.house.orderTaskables()

        self.house.store.changeStamp(0.0)
        self.assertEqual(logger.stamp, 0.0)

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.ALWAYS)

        self.assertEqual(log.baseFilename, log.name)
        self.assertEqual(log.path, '')
        self.assertEqual(log.file, None)
        self.assertEqual(log.kind, 'text')

        self.assertEqual(log.rule, globaling.ALWAYS)
        self.assertEqual(log.action, log.always)

        logger.addLog(log)

        heading = self.store.create('pose.heading').create(value = 0.0)
        #position = self.store.create('pose.position').create([("north", 10.0), ("east", 5.0)])

        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        #log.addLoggee(tag = 'pos', loggee = 'pose.position')

        logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)

        status = logger.runner.send(globaling.START)  # reopens prepares and logs once

        self.assertTrue(logger.path.startswith('/tmp/log/ioflo/HouseTest/LoggerTest'))
        self.assertTrue(log.path.startswith(logger.path))
        self.assertTrue(log.path.endswith(log.baseFilename + '.txt'))
        self.assertTrue(log.file)

        self.assertEqual(len(log.paths), keep+1)
        for k, path in enumerate(log.paths[1:]):
            self.assertTrue(path.startswith(logger.path))
            base = os.path.basename(path)
            root, ext = os.path.splitext(base)
            self.assertTrue(root.endswith("{0:02}".format(k+1)))

        for i in range(16):
            self.store.advanceStamp(0.125)
            heading.value += 1.0
            status = logger.runner.send(globaling.RUN)

        self.store.advanceStamp(0.125)
        heading.value += 1.0
        status = logger.runner.send(globaling.STOP)  # logs once and closes logs

        path0, path1, path2 = log.paths

        file0 = open(path0, "r")
        lines = file0.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                 '_time\theading\n',
                                 '2.125\t17.0\n'])
        file0.close()

        file1 = open(path1, "r")
        lines = file1.readlines()
        self.assertEqual(lines,['text\tAlways\ttest\n',
                                '_time\theading\n',
                                '1.625\t13.0\n',
                                '1.75\t14.0\n',
                                '1.875\t15.0\n',
                                '2.0\t16.0\n'] )
        file1.close()

        file2 = open(path2, "r")
        lines = file2.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                '_time\theading\n',
                                '1.125\t9.0\n',
                                '1.25\t10.0\n',
                                '1.375\t11.0\n',
                                '1.5\t12.0\n'])
        file2.close()

        # restart for reuse
        status = logger.runner.send(globaling.START)  # reopens prepares and logs once

        self.assertTrue(logger.path.startswith('/tmp/log/ioflo/HouseTest/LoggerTest'))
        self.assertTrue(log.path.startswith(logger.path))
        self.assertTrue(log.path.endswith(log.baseFilename + '.txt'))
        self.assertTrue(log.file)

        self.assertEqual(len(log.paths), keep+1)
        for k, path in enumerate(log.paths[1:]):
            self.assertTrue(path.startswith(logger.path))
            base = os.path.basename(path)
            root, ext = os.path.splitext(base)
            self.assertTrue(root.endswith("{0:02}".format(k+1)))

        for i in range(3):
            self.store.advanceStamp(0.125)
            heading.value += 1.0
            status = logger.runner.send(globaling.RUN)

        self.store.advanceStamp(0.125)
        heading.value += 1.0
        status = logger.runner.send(globaling.STOP)  # logs once and closes logs

        path0, path1, path2 = log.paths

        file0 = open(path0, "r")
        lines = file0.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                 '_time\theading\n',
                                 '2.625\t21.0\n'])
        file0.close()

        file1 = open(path1, "r")
        lines = file1.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                '_time\theading\n',
                                '2.125\t17.0\n',
                                '2.125\t17.0\n',
                                '2.25\t18.0\n',
                                '2.375\t19.0\n',
                                '2.5\t20.0\n'])
        file1.close()

        file2 = open(path2, "r")
        lines = file2.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                '_time\theading\n',
                                '1.625\t13.0\n',
                                '1.75\t14.0\n',
                                '1.875\t15.0\n',
                                '2.0\t16.0\n'])
        file2.close()

        for path in log.paths:  # remove files to clean up
            try:
                os.remove(path)
            except OSError as ex:
                pass

    def testReuse(self):
        """
        Test logger with non unique directory name
        """
        console.terse("{0}\n".format(self.testReuse.__doc__))
        self.assertEqual(self.house.store, self.store)

        prefix = "/tmp/log/ioflo"
        flush = 3.0
        logger = logging.Logger(name="LoggerTest",
                                store=self.store,
                                schedule=globaling.ACTIVE,
                                prefix=prefix,
                                flushPeriod=flush,
                                reuse=True)

        self.assertEqual(logger.flushPeriod, flush)
        self.assertEqual(logger.prefix, '/tmp/log/ioflo')
        self.assertTrue(logger.runner)  # runner generator is made when logger created
        self.assertEqual(logger.cyclePeriod, 0)
        self.assertEqual(logger.keep, 0)
        self.assertEqual(logger.fileSize, 0)
        self.assertEqual(logger.cycleStamp, 0.0)
        self.assertEqual(logger.flushStamp, 0.0)
        self.assertEqual(logger.path, '')
        self.assertTrue(logger.reuse)

        self.assertEqual(logger.logs, [])

        self.house.taskers.append(logger)
        self.house.mids.append(logger)
        self.house.orderTaskables()

        self.house.store.changeStamp(0.0)
        self.assertEqual(logger.stamp, 0.0)

        log = logging.Log(name='test',
                          store=self.store,
                          kind='text',
                          baseFileName='',
                          rule=globaling.ALWAYS)

        self.assertEqual(log.baseFilename, log.name)
        self.assertEqual(log.path, '')
        self.assertEqual(log.file, None)
        self.assertEqual(log.kind, 'text')

        self.assertEqual(log.rule, globaling.ALWAYS)
        self.assertEqual(log.action, log.always)

        logger.addLog(log)

        heading = self.store.create('pose.heading').create(value = 0.0)
        #position = self.store.create('pose.position').create([("north", 10.0), ("east", 5.0)])

        log.addLoggee(tag = 'heading', loggee = 'pose.heading')
        #log.addLoggee(tag = 'pos', loggee = 'pose.position')

        logger.resolve()  # resolves logs as well

        self.house.store.changeStamp(0.0)
        self.assertIs(log.stamp, None)

        status = logger.runner.send(globaling.START)  # reopens prepares and logs once

        self.assertTrue(logger.path.startswith('/tmp/log/ioflo/HouseTest/LoggerTest'))
        self.assertTrue(log.path.startswith(logger.path))
        self.assertTrue(log.path.endswith(log.baseFilename + '.txt'))
        self.assertTrue(log.file)

        self.assertEqual(len(log.paths), 0)

        for i in range(16):
            self.store.advanceStamp(0.125)
            heading.value += 1.0
            status = logger.runner.send(globaling.RUN)

        self.store.advanceStamp(0.125)
        heading.value += 1.0
        status = logger.runner.send(globaling.STOP)  # logs once and closes logs

        file = open(log.path, "r")
        lines = file.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                '_time\theading\n',
                                '0.0\t0.0\n',
                                '0.125\t1.0\n',
                                '0.25\t2.0\n',
                                '0.375\t3.0\n',
                                '0.5\t4.0\n',
                                '0.625\t5.0\n',
                                '0.75\t6.0\n',
                                '0.875\t7.0\n',
                                '1.0\t8.0\n',
                                '1.125\t9.0\n',
                                '1.25\t10.0\n',
                                '1.375\t11.0\n',
                                '1.5\t12.0\n',
                                '1.625\t13.0\n',
                                '1.75\t14.0\n',
                                '1.875\t15.0\n',
                                '2.0\t16.0\n',
                                '2.125\t17.0\n'])
        file.close()

        # restart for reuse
        self.house.store.changeStamp(0.0)
        log.stamp = None
        self.assertIs(log.stamp, None)

        status = logger.runner.send(globaling.START)  # reopens prepares and logs once

        self.assertTrue(logger.path.startswith('/tmp/log/ioflo/HouseTest/LoggerTest'))
        self.assertTrue(log.path.startswith(logger.path))
        self.assertTrue(log.path.endswith(log.baseFilename + '.txt'))
        self.assertTrue(log.file)

        self.assertEqual(len(log.paths), 0)

        status = logger.runner.send(globaling.START)  # reopens prepares and logs once

        self.assertTrue(logger.path.startswith('/tmp/log/ioflo/HouseTest/LoggerTest'))
        self.assertTrue(log.path.startswith(logger.path))
        self.assertTrue(log.path.endswith(log.baseFilename + '.txt'))
        self.assertTrue(log.file)

        self.assertEqual(len(log.paths), 0)

        for i in range(3):
            self.store.advanceStamp(0.125)
            heading.value += 1.0
            status = logger.runner.send(globaling.RUN)

        self.store.advanceStamp(0.125)
        heading.value += 1.0
        status = logger.runner.send(globaling.STOP)  # logs once and closes logs

        file = open(log.path, "r")
        lines = file.readlines()
        self.assertEqual(lines, ['text\tAlways\ttest\n',
                                '_time\theading\n',
                                '0.0\t0.0\n',
                                '0.125\t1.0\n',
                                '0.25\t2.0\n',
                                '0.375\t3.0\n',
                                '0.5\t4.0\n',
                                '0.625\t5.0\n',
                                '0.75\t6.0\n',
                                '0.875\t7.0\n',
                                '1.0\t8.0\n',
                                '1.125\t9.0\n',
                                '1.25\t10.0\n',
                                '1.375\t11.0\n',
                                '1.5\t12.0\n',
                                '1.625\t13.0\n',
                                '1.75\t14.0\n',
                                '1.875\t15.0\n',
                                '2.0\t16.0\n',
                                '2.125\t17.0\n',
                                '0.0\t17.0\n',
                                '0.0\t17.0\n',
                                '0.125\t18.0\n',
                                '0.25\t19.0\n',
                                '0.375\t20.0\n',
                                '0.5\t21.0\n'])
        file.close()

        try:
            os.remove(log.path)  # remove to clean up
        except OSError as ex:
            pass


def runOneLogger(test):
    '''
    Unittest Runner
    '''
    test = LoggerTestCase(test)
    suite = unittest.TestSuite([test])
    unittest.TextTestRunner(verbosity=2).run(suite)

def runOneHouse(test):
    '''
    Unittest Runner
    '''
    test = HouseTestCase(test)
    suite = unittest.TestSuite([test])
    unittest.TextTestRunner(verbosity=2).run(suite)

def runSome():
    """ Unittest runner """
    tests =  []
    names = [
                'testLogger',
                'testLogAlways',
                'testLogOnce',
                'testLogNever',
                'testLogUpdate',
                'testLogUpdateFields',
                'testLogChange',
                'testLogChangeFields',
                'testLogStreak',
                'testLogStreakFields',
                'testLogDeck',
            ]
    tests.extend(map(LoggerTestCase, names))

    names = [
                'testSetup',
                'testCycle',
                'testCycleReuse',
                'testReuse',
            ]
    tests.extend(map(HouseTestCase, names))

    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

def runAll():
    """ Unittest runner """
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(LoggerTestCase))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(HouseTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__' and __package__ is None:

    #console.reinit(verbosity=console.Wordage.concise)

    #runAll() #run all unittests

    runSome()#only run some

    #runOneLogger('testLogStreak')
    #runOneHouse('testCycleReuse')
