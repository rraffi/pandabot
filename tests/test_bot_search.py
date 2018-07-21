#!/usr/bin/env python
# -*- coding: utf8 -*-
import unittest
import logging
import random
from flask_migrate import upgrade
from flask_migrate import Migrate
from tests.test_base import TestBase

class TestBotSearch(TestBase):

    def setUp(self):
        super(TestBotSearch, self).setUp()
        # suppress logging
        logging.disable(logging.CRITICAL)
        # run the database migrations
        Migrate(self.app, self.db)
        upgrade()

    def tearDown(self):
        super(TestBotSearch, self).tearDown()
        logging.disable(logging.NOTSET)

    def test_suggestions_made_when_no_match_found(self):
        ''' When a definition is requested for a term that isn't in the database, a list
            of suggestions is returned.
        '''
        # set some definitions
        # this is the order the matches should be returned in
        matches = [
            ("abglosscd", "a cool thing"),
            ("glossed gloss", "a really useful tool"),
            ("standard gloss", "a good resource"),
            ("dictionary helper", "a gloss that is really glossing my world"),
            ("luster", "a prominent gloss")
        ]
        # set the definitions in random order
        randomized_matches = list(matches)
        random.shuffle(randomized_matches)
        for post_match in randomized_matches:
            self.post_command(text="{} = {}".format(post_match[0], post_match[1]))

        # request a definition that doesn't exist, but that will generate suggestions
        robo_response = self.post_command(text="shh gloss")
        match_text = ', '.join(['*{}*'.format(item[0]) for item in matches])
        self.assertTrue(match_text.encode('utf-8') in robo_response.data)

    def test_search_results(self):
        ''' A search of terms and definitions returns the expected results.
        '''
        # set some definitions
        matches = [
            ("CalWIN", "CalWORKs Information Network, a service supporting the administration of public assistance programs in a consortium of California counties, including CalFresh, Medi-Cal, General Assistance, and Foster Care. Part of SAWS."),
            ("TAY", "Transitional Age Youth, people between the ages of sixteen and twenty-four who are in transition from state custody or foster care and are at-risk."),
            ("SAWS", "the Statewide Automated Welfare System, made up of multiple systems (including C-IV, CalWin and LEADER) which support eligibility and benefit determination, enrollment, and case maintenance at the county level for some of California's major health and human services programs."),
            ("WIB", "Workforce Investment Board, a regional entity created to implement the Workforce Investment Act of 1998 by directing federal, state and local funding to workforce development programs."),
            ("ACYF", "Administration for Children, Youth and Families, a part of the Administration for Children and Families, under the Department of Health and Human Services, administered by a commissioner who is a presidential appointee. ACYF is divided into two bureaus: the Children's Bureau and the Family and Youth Services Bureau, each of which is responsible for different issues involving children, youth and families and with a cross-cutting unit responsible for research and evaluation.")
        ]
        # set the definitions in random order
        randomized_matches = list(matches)
        random.shuffle(randomized_matches)
        for post_match in randomized_matches:
            self.post_command(text="{} = {}".format(post_match[0], post_match[1]))

        # make some searchs and verify that they come back as expected
        robo_response = self.post_command(text="search youth")
        self.assertTrue('found *youth* in: *ACYF*, *TAY*'.encode('utf-8') in robo_response.data)

        robo_response = self.post_command(text="search saws")
        self.assertTrue('found *saws* in: *SAWS*, *CalWIN*'.encode('utf-8') in robo_response.data)

        robo_response = self.post_command(text="search calwin")
        self.assertTrue('found *calwin* in: *CalWIN*, *SAWS*'.encode('utf-8') in robo_response.data)

        robo_response = self.post_command(text="search state")
        self.assertTrue('*TAY*'.encode('utf-8') in robo_response.data)
        self.assertTrue('*WIB*'.encode('utf-8') in robo_response.data)

        robo_response = self.post_command(text="search banana")
        self.assertTrue('could not find *banana* in any terms or definitions.'.encode('utf-8') in robo_response.data)

if __name__ == '__main__':
    unittest.main()
