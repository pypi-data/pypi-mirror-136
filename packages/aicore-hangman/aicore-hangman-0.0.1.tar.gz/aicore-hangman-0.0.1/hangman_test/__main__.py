from hangman.hangman_solution import Hangman
from hangman.hangman_solution import play_game
import unittest
from contextlib import redirect_stdout
import io
from unittest.mock import patch, call

class HangmanTestCase(unittest.TestCase):
    currentResult = None # holds last result object passed to run method
    longMessage = False

    def setUp(self):
        word_list = ['WatermelonBanana']
        f = io.StringIO()
        with redirect_stdout(f):
            self.game = Hangman(word_list, 5)
        self.init_message = f.getvalue()

    @classmethod
    def setResult(cls, amount, errors, failures, skipped):
        cls.amount, cls.errors, cls.failures, cls.skipped = \
            amount, errors, failures, skipped

    def tearDown(self):
        amount = self.currentResult.testsRun
        errors = self.currentResult.errors
        failures = self.currentResult.failures
        skipped = self.currentResult.skipped
        self.setResult(amount, errors, failures, skipped)

    @classmethod
    def tearDownClass(cls):
        print("tests run: " + str(cls.amount))
        print("errors: " + str(len(cls.errors)))
        print("failures: " + str(len(cls.failures)))
        print("success: " + str(cls.amount - len(cls.errors) - len(cls.failures)))
        print("skipped: " + str(len(cls.skipped)))

    def run(self, result=None):
        self.currentResult = result # remember result for use in tearDown
        unittest.TestCase.run(self, result) # call superclass run method 
    
    def test_init(self):
        self.assertEqual(self.init_message, "The mistery word has 16 characters\n['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_']\n")

    def test_word(self):
        self.assertEqual(self.game.word, 'WatermelonBanana', 'The word attribute is not properly set')
        self.assertEqual(self.game.num_letters, len(set(self.game.word)), 'The num_letters attribute is not properly set')
    
    def test_word_guessed(self):
        self.assertEqual(self.game.word_guessed, ['_'] * len(self.game.word), 'The word_guessed attribute is not properly set')
        
    def test_num_lives_exists(self):
        self.assertTrue(hasattr(self.game, 'num_lives'), 'The num_lives attribute does not exist')

    def test_num_lives(self):
        self.assertEqual(self.game.num_lives, 5, 'The num_lives attribute is not properly set')

    def test_check_ask_letter_right(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with unittest.mock.patch('builtins.input', return_value='a'):
                self.game.ask_letter()
            message = f.getvalue()
        
        expected_message = "Nice! a is in the word!\n['_', 'a', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'a', '_', 'a', '_', 'a']\n"
        self.assertEqual(message, expected_message, 'The check_ask_letter method is not working properly, check that the message has the right format')

    def test_check_ask_letter_wrong_guess(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with unittest.mock.patch('builtins.input', return_value='z'):
                self.game.ask_letter()
            message = f.getvalue()
        
        expected_message = "Sorry, z is not in the word.\nYou have 4 lives left.\n"
        self.assertEqual(message, expected_message, 'The check_ask_letter method is not working properly. Check that the message has the right format')

    @patch('builtins.input', side_effect=['aaa'])
    def test_check_invalid(self, input_mock):
        f = io.StringIO()
        with redirect_stdout(f):
            with self.assertRaises(Exception) as context:
      
                self.game.ask_letter()
            actual_value = f.getvalue()
        expected = 'Please, enter just one character\n'
        self.assertEqual(actual_value, expected, 'The ask_letter method is not checking for invalid input. If it does, make sure that the message has the right format')

    def test_check_repeated(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', return_value='a') as input_mock:
                self.game.ask_letter()
            # actual_value = f.getvalue()
        f = io.StringIO()
        with redirect_stdout(f):  
            with self.assertRaises(Exception) as context:
                with patch('builtins.input', side_effect=['a']) as input_mock:
                    self.game.ask_letter()
            actual_value = f.getvalue()
        expected = 'a was already tried\n'
        self.assertEqual(actual_value, expected, 'The ask_letter method is not checking for repeated words. If it does, make sure that the message has the right format')


    def test_uppercase(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', return_value='W') as input_mock:
                self.game.ask_letter()
            actual_value = f.getvalue()
        expected = "Nice! w is in the word!\n['w', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_']\n"
        self.assertEqual(actual_value, expected, 'The application should not discern between uppercased and lowercased letters. Make sure you normalize the words')

    def test_play_win(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', side_effect=['W', 'a', 't', 'e', 'r', 'm', 'l', 'o', 'n', 'b']) as input_mock:
                play_game(['WatermelonBanana'])
        actual_value = f.getvalue()
        actual_last = actual_value.split('\n')[-2]
        expected = "Congratulations, you won!"
        self.assertEqual(actual_last, expected, 'The play_game method is not working properly. Check that the message has the right format')

    def test_play_lose(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with patch('builtins.input', side_effect=['z', 's', 'p', 'q', 'v']) as input_mock:
                play_game(['WatermelonBanana'])
        actual_value = f.getvalue()
        actual_last = actual_value.split('\n')[-2]
        expected = "You ran out of lives. The word was WatermelonBanana"
        self.assertEqual(actual_last, expected, 'The play_game method is not working properly. Check that the message has the right format')

if __name__ == '__main__':

    unittest.main(verbosity=0)
    