def guess(self, word, fivegram, fourgram, trigram, bigram, unigram):
    # word input example: "_ p p _ e "

      ################################################
      ## Replace with your own "guess" function here #
      ################################################

        # clean the word so that we strip away the space characters
          clean_word = word[::2]

        # a list of incorrect guesses to update the ngrams
          self.incorrect_guesses = list(set(self.guessed_letters) - set(word))

        # reconfiguring only if the last guess was incorrect and number of guesses remaining are less.
        # this ensures that the analysis adapts and updates based on the user's feedback and the game's progress.
          if len(self.guessed_letters) > 0 and self.guessed_letters[-1] in self.incorrect_guesses:
             self.reoptimize_ngrams()

        # reseting the probabilities to zero from the last guess
          self.probabilities = [0] * len(self.letter_set)

        # run through ngram function
          return self.fivegram_probability(clean_word, fivegram, fourgram, trigram, bigram, unigram)


    def build_ngram_models(self, dictionary):

      # create a nested dictionary that stores the occurrences of letter sequences ranging from 1 to 5 characters in length.
      # the nested dictionary will have an additional level to account for the length of each word in unigrams and bigrams.
      # for the unigram level, consider only the unique letters within each word.

      unigram = collections.defaultdict(lambda: collections.defaultdict(int))
      bigram = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
      trigram = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
      fourgram = collections.defaultdict(lambda:collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int))))
      fivegram = collections.defaultdict(lambda: collections.defaultdict(lambda:collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))))

      # iterating through each word in the dictionary
      # count the occurrences of letter sequences in words from the dictionary and update the n-gram models accordingly.
      for word in dictionary:
          # check each letter in the dictionary and update the ngram
          for i in range(len(word) - 4):
              # We exclude the last four letters of the word because it is searching for patterns of
              # four consecutive letters with a blank in the fifth position. Since the last four letters
              # cannot form such a pattern, there is no need to check them, resulting in improved efficiency
              # and focusing on the relevant parts of the word.

              bigram[len(word)][word[i]][word[i+1]] += 1
              trigram[word[i]][word[i+1]][word[i+2]] += 1
              fourgram[word[i]][word[i+1]][word[i+2]][word[i+3]] += 1
              fivegram[word[i]][word[i+1]][word[i+2]][word[i+3]][word[i+4]] += 1

          i = len(word) - 4

          # fill rest of the ngrams for words very small words and complete coverage
          if len(word) == 2:
              bigram[len(word)][word[0]][word[1]] += 1
          elif len(word) == 3:
              bigram[len(word)][word[0]][word[1]] += 1
              bigram[len(word)][word[1]][word[2]] += 1
              trigram[word[0]][word[1]][word[2]] += 1
          # fill out rest of the fourgrams
          elif len(word) >= 4:
              bigram[len(word)][word[i]][word[i+1]] += 1
              bigram[len(word)][word[i+1]][word[i+2]] += 1
              bigram[len(word)][word[i+2]][word[i+3]] += 1
              trigram[word[i]][word[i+1]][word[i+2]] += 1
              trigram[word[i+1]][word[i+2]][word[i+3]] += 1
              fourgram[word[i]][word[i+1]][word[i+2]][word[i+3]] += 1

          # fill out unigrams
          for letter in set(word):
              unigram[len(word)][letter] += 1

      return unigram, bigram, trigram, fourgram, fivegram

    #when there is error
    def reoptimize_ngrams(self):

      # regulates the ngrams after removing any incorrectly guessed letters
      # updates the dictionary to eliminate words containing incorrectly guessed letters
      new_dictionary = [word for word in self.full_dictionary if not set(word).intersection(set(self.incorrect_guesses))]
      self.unigram, self.bigram, self.trigram, self.fourgram, self.fivegram = self.build_ngram_models(new_dictionary)


    def fivegram_probability(self, word, fivegram, fourgram, trigram, bigram, unigram):

      #given an input word in a clean format with no spaces and placeholders ('_') for unknown letters,
      #the process utilizes tri-grams to determine the likelihood of a specific letter appearing in a five-letter sequence for a word of a given length.
      #the output provides the probabilities for each letter, which will be utilized in the subsequent stage.

      # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)

        total_count = 0
        letter_count = [0] * len(self.letter_set)

        # traverse the word and find patterns that have three consecutive letters where one of them is blank
        for i in range(len(word) - 4):
          # We exclude the last four letters of the word because it is searching for patterns of
          # four consecutive letters with a blank in the fifth position. Since the last four letters
          # cannot form such a pattern, there is no need to check them, resulting in improved efficiency
          # and focusing on the relevant parts of the word.

            # case 1: "eg word:  xyzw_ "
            if word[i] != '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] != '_' and word[i+4] == '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+1]
                anchor_letter3 = word[i+2]
                anchor_letter4 = word[i+3]

                # calculate occurences of "anchor_letter1 anchor_letter2 blank" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[anchor_letter1][anchor_letter2][anchor_letter3][anchor_letter4][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[anchor_letter1][anchor_letter2][anchor_letter3][anchor_letter4][letter]
                        letter_count[j] += self.fivegram[anchor_letter1][anchor_letter2][anchor_letter3][anchor_letter4][letter]

            # case 2: "eg word: xyz_w "
            elif word[i] != '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] == '_' and word[i+4] != '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+1]
                anchor_letter3 = word[i+2]
                anchor_letter4 = word[i+4]

                # calculate occurences of "anchor_letter1 blank anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[anchor_letter1][anchor_letter2][anchor_letter3][letter][anchor_letter4] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[anchor_letter1][anchor_letter2][anchor_letter3][letter][anchor_letter4]
                        letter_count[j] += self.fivegram[anchor_letter1][anchor_letter2][anchor_letter3][letter][anchor_letter4]

            # case 3: "eg word: wx_yz "
            elif word[i] != '_' and word[i+1] != '_' and word[i+2] == '_' and word[i+3] != '_' and word[i+4] != '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+1]
                anchor_letter3 = word[i+3]
                anchor_letter4 = word[i+4]

                # calculate occurences of "blank anchor_letter1 anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[anchor_letter1][anchor_letter2][letter][anchor_letter3][anchor_letter4] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[anchor_letter1][anchor_letter2][letter][anchor_letter3][anchor_letter4]
                        letter_count[j] += self.fivegram[anchor_letter1][anchor_letter2][letter][anchor_letter3][anchor_letter4]

            # case 4: "eg word: x_wyz"
            elif word[i] != '_' and word[i+1] == '_' and word[i+2] != '_' and word[i+3] != '_' and word[i+4] != '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+2]
                anchor_letter3 = word[i+3]
                anchor_letter4 = word[i+4]

                # calculate occurences of "blank anchor_letter1 anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[anchor_letter1][letter][anchor_letter2][anchor_letter3][anchor_letter4] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[anchor_letter1][letter][anchor_letter2][anchor_letter3][anchor_letter4]
                        letter_count[j] += self.fivegram[anchor_letter1][letter][anchor_letter2][anchor_letter3][anchor_letter4]

            # case 5: "eg word: _xwyz"
            elif word[i] == '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] != '_' and word[i+4] != '_':
                anchor_letter1 = word[i+1]
                anchor_letter2 = word[i+2]
                anchor_letter3 = word[i+3]
                anchor_letter4 = word[i+4]

                # calculate occurences of "blank anchor_letter1 anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[letter][anchor_letter1][anchor_letter2][anchor_letter3][anchor_letter4] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[letter][anchor_letter1][anchor_letter2][anchor_letter3][anchor_letter4]
                        letter_count[j] += self.fivegram[letter][anchor_letter1][anchor_letter2][anchor_letter3][anchor_letter4]

        # calculate the probabilities of each letter
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count

        # interpolate probabilities between trigram and bigram
        """
       The step of multiplying each probability in probs by 0.40 and adding it to
       the corresponding probability in self.probabilities depicts interpolation.
       It is performed to combine the probabilities obtained from the fivegram level with the
       existing probabilities from the previous levels (trigram and bigram).This interpolation
       helps to balance the influence of higher-level ngrams (trigrams and bigrams) with the
       more specific information provided by the fivegram model.The method assigns a lower weight
       to the probabilities derived from the fivegram model. The factor of 0.40 determines the
       weight assigned to the fivegram probabilities, while the remaining weight (0.60) is assigned
       to the existing probabilities in self.probabilities. Overall, the interpolation step helps in
       combining the information from different ngram models to make more accurate predictions about
       the likelihood of specific letters appearing in the target blank space, considering both local
       and global patterns in the word.
        """

        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (fivegram)

        # go for the next level
        return self.fourgram_probability(word, fivegram, fourgram, trigram, bigram, unigram)

    def fourgram_probability(self, word, fivegram, fourgram, trigram, bigram, unigram):

      # given a word in a clean format without spaces and placeholders ('_') for unknown letters,
      # the process utilizes tri-grams to determine the probabilities of specific letters appearing in a four-letter sequence for a word of a given length.
      # the output provides the probabilities for each letter, which will be utilized in the next stage.


        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)

        total_count = 0
        letter_count = [0] * len(self.letter_set)

        # calculates the probabilities of each letter in a word based on its context using a four-gram model.
        # It considers different cases based on the positions of underscores (_) in the word and updates the letter probabilities accordingly.
        # The probabilities are then interpolated with the existing probabilities from lower-level n-gram models (trigram and bigram)
        # to balance the influence of higher-level n-grams. The function then proceeds to the next level of the n-gram model to further
        # calculate the probabilities.

        # traverse the word and find patterns that have three consecutive letters where one of them is blank
        for i in range(len(word) - 3):

            # case 1: "eg word: abc_"
            if word[i] != '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] == '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+1]
                anchor_letter3 = word[i+2]

                # calculate occurences of "anchor_letter1 anchor_letter2 blank" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fourgram[anchor_letter1][anchor_letter2][anchor_letter3][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.fourgram[anchor_letter1][anchor_letter2][anchor_letter3][letter]
                        letter_count[j] += self.fourgram[anchor_letter1][anchor_letter2][anchor_letter3][letter]

            # case 2:  "eg word: ab_c"
            elif word[i] != '_' and word[i+1] != '_' and word[i+2] == '_' and word[i+3] != '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+1]
                anchor_letter3 = word[i+3]

                # calculate occurences of "anchor_letter1 blank anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fourgram[anchor_letter1][anchor_letter2][letter][anchor_letter3] > 0 and letter not in self.guessed_letters:
                        total_count += self.fourgram[anchor_letter1][anchor_letter2][letter][anchor_letter3]
                        letter_count[j] += self.fourgram[anchor_letter1][anchor_letter2][letter][anchor_letter3]

            # case 3: "eg word: a_bc"
            elif word[i] != '_' and word[i+1] == '_' and word[i+2] != '_' and word[i+3] != '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+2]
                anchor_letter3 = word[i+3]

                # calculate occurences of "blank anchor_letter1 anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fourgram[anchor_letter1][letter][anchor_letter2][anchor_letter3] > 0 and letter not in self.guessed_letters:
                        total_count += self.fourgram[anchor_letter1][letter][anchor_letter2][anchor_letter3]
                        letter_count[j] += self.fourgram[anchor_letter1][letter][anchor_letter2][anchor_letter3]

            # case 4:  "eg word: _abc"
            elif word[i] == '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] != '_':
                anchor_letter1 = word[i+1]
                anchor_letter2 = word[i+2]
                anchor_letter3 = word[i+3]

                # calculate occurences of "blank anchor_letter1 anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fourgram[letter][anchor_letter1][anchor_letter2][anchor_letter3] > 0 and letter not in self.guessed_letters:
                        total_count += self.fourgram[letter][anchor_letter1][anchor_letter2][anchor_letter3]
                        letter_count[j] += self.fourgram[letter][anchor_letter1][anchor_letter2][anchor_letter3]

        # calculate the probabilities of each letter
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count

        # interpolate probabilities between trigram and bigram

        """
        Multiply each probability in probs by 0.25 and add it to the corresponding probability in self.probabilities.
        This interpolation step combines the probabilities obtained from the fourgram model with the existing
        probabilities from the previous levels (trigram and bigram). It balances the influence of higher-level
        ngrams with the more specific information provided by the fourgram model.
        """
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (fourgram)

        # go for the next level
        return self.trigram_probability(word, fivegram, fourgram, trigram, bigram, unigram)

    def trigram_probability(self, word, fivegram, fourgram, trigram, bigram, unigram):

      # given a word in a clean format without spaces and placeholders ('_') for unknown letters,
      # the process utilizes tri-grams to determine the probabilities of specific letters appearing in a three-letter sequence for a word of a given length.
      # the output provides the probabilities for each letter, which will be utilized in the next stage.

        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)

        total_count = 0
        letter_count = [0] * len(self.letter_set)

        # traverse the word and find patterns that have three consecutive letters where one of them is blank
        for i in range(len(word) - 2):

            # case 1: "eg word: ab_"
            if word[i] != '_' and word[i+1] != '_' and word[i+2] == '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+1]

                # calculate occurences of "anchor_letter1 anchor_letter2 blank" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.trigram[anchor_letter1][anchor_letter2][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.trigram[anchor_letter1][anchor_letter2][letter]
                        letter_count[j] += self.trigram[anchor_letter1][anchor_letter2][letter]

            # case 2: "eg word: a_b"
            elif word[i] != '_' and word[i+1] == '_' and word[i+2] != '_':
                anchor_letter1 = word[i]
                anchor_letter2 = word[i+2]

                # calculate occurences of "anchor_letter1 blank anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.trigram[anchor_letter1][letter][anchor_letter2] > 0 and letter not in self.guessed_letters:
                        total_count += self.trigram[anchor_letter1][letter][anchor_letter2]
                        letter_count[j] += self.trigram[anchor_letter1][letter][anchor_letter2]

            # case 3: "eg word: _ab"
            elif word[i] == '_' and word[i+1] != '_' and word[i+2] != '_':
                anchor_letter1 = word[i+1]
                anchor_letter2 = word[i+2]

                # calculate occurences of "blank anchor_letter1 anchor_letter2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.trigram[letter][anchor_letter1][anchor_letter2] > 0 and letter not in self.guessed_letters:
                        total_count += self.trigram[letter][anchor_letter1][anchor_letter2]
                        letter_count[j] += self.trigram[letter][anchor_letter1][anchor_letter2]

        # calculate the probabilities of each letter
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count

        # interpolate probabilities between trigram and bigram

        """
        Multiply each probability in probs by 0.20 and add it to the corresponding probability in self.probabilities.
        This interpolation step combines the probabilities obtained from the trigram model with the existing
        probabilities from the previous levels. It balances the influence of higher-level
        ngrams with the more specific information provided by the trigram model.
        """
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (trigram)

        # go for the next level
        return self.bigram_probability(word, fivegram, fourgram, trigram, bigram, unigram)


    def bigram_probability(self, word, fivegram, fourgram, trigram, bigram, unigram):

      #given a word in a clean format without spaces and placeholders ('_') for unknown letters,
      #the process utilizes bi-grams to determine the probabilities of specific letters appearing in a two-letter sequence for a word of a given length.
      #these probabilities are then updated in the trigram_probability set.
      #the output provides the probabilities for each letter, which will be used in the next stage.

        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)

        total_count = 0
        letter_count = [0] * len(self.letter_set)

        # traverse the word and find either patterns of "letter blank" or "blank letter"
        for i in range(len(word) - 1):
            # case 1: "eg word: a_"
            if word[i] != '_' and word[i+1] == '_':
                anchor_letter = word[i]

                # calculate occurences of "anchor_letter blank" and each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.bigram[len(word)][anchor_letter][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.bigram[len(word)][anchor_letter][letter]
                        letter_count[j] += self.bigram[len(word)][anchor_letter][letter]

            # case 2: "eg word: _a"
            elif word[i] == '_' and word[i+1]!= '_':
                anchor_letter = word[i+1]

                # calculate occurences of "blank anchor_letter" and each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.bigram[len(word)][letter][anchor_letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.bigram[len(word)][letter][anchor_letter]
                        letter_count[j] += self.bigram[len(word)][letter][anchor_letter]

        # calculate the probabilities of each letter
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count

        # interpolate probabilities between trigram and bigram
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (bigram)

        # return letter associated with highest probability
        return self.unigram_probability(word, fivegram, fourgram, trigram, bigram, unigram)


    def unigram_probability(self, word, fivegram, fourgram, trigram, bigram, unigram):

      # given a word in a clean format without spaces and placeholders ('_') for unknown letters,
      # the process utilizes unigrams to calculate the probabilities of specific letters appearing in any blank space.
      # These probabilities are then updated in the bigram_probability set.
      # The output provides the letter with the highest overall probability.

        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)

        total_count = 0
        letter_count = [0] * len(self.letter_set)

        # traverse the word and find blank spaces
        for i in range(len(word)):
            # case 1: "eg word: a_"
            if word[i] == '_':

                # calculate occurences of pattern and each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.unigram[len(word)][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.unigram[len(word)][letter]
                        letter_count[j] += self.unigram[len(word)][letter]

        # calculate the probabilities of each letter appearing
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count

        # interpolate probabilities
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (unigram)

        # adjust probabilities so they sum to one
        final_probs = [0] * len(self.letter_set)
        if sum(self.probabilities) > 0:
            for i in range(len(self.probabilities)):
                final_probs[i] = self.probabilities[i] / sum(self.probabilities)

        self.probabilities = final_probs

        # finding letter with highest probability
        max_prob = 0
        guess_letter = ''
        for i, letter in enumerate(self.letter_set):
            if self.probabilities[i] > max_prob:
                max_prob = self.probabilities[i]
                guess_letter = letter

        letters_table = {
            1: ['a', 'i'],
            2: ['a', 'o', 'e', 'i', 'm', 'h', 'n', 'u', 's', 't', 'y', 'b', 'l', 'p', 'x', 'd', 'f', 'r', 'w', 'w', 'g', 'j', 'k'],
            3: ['a', 'e', 'o', 'i', 't', 's', 'u', 'p', 'r', 'n', 'd', 'b', 'g', 'm', 'y', 'l', 'h', 'w', 'f', 'c', 'k', 'x', 'v', 'j', 'z', 'q'],
            4: ['a', 'e', 's', 'o', 'i', 'r', 'l', 't', 'n', 'u', 'd', 'p', 'm', 'h', 'c', 'b', 'k', 'g', 'y', 'w', 'f', 'v', 'j', 'z', 'x', 'q'],
            5: ['s', 'e', 'a', 'r', 'o', 'i', 'l', 't', 'n', 'u', 'd', 'c', 'y', 'p', 'm', 'h', 'g', 'b', 'k', 'f', 'w', 'v', 'z', 'x', 'j', 'q'],
            6: ['e', 's', 'a', 'r', 'n', 'o', 't', 'n', 't', 'd', 'u', 'g', 'p', 'm', 'h', 'h', 'b', 'f', 'k', 'v'],
            7: ['e', 's', 'i', 'a', 'n', 'n', 't', 'o', 'l', 'c', 'u', 'g', 'm', 'p', 'h', 'h', 'b', 'f', 'v'],
            8: ['e', 's', 'i', 'a', 's', 'n', 't', 'o', 'l', 'c', 'u', 'g', 'm', 'p', 'h', 'h', 'b', 'f', 'v'],
            9: ['e', 's', 'i', 'r', 'a', 'n', 't', 'o', 'l', 'c', 'd', 'g', 'm', 'p', 'h', 'h', 'b', 'f', 'v'],
            10: ['e', 's', 'i', 'r', 'a', 'r', 't', 'o', 'l', 'c', 'd', 'g', 'm', 'p', 'h', 'h', 'b', 'f', 'v'],
            11: ['e', 'i', 'i', 'n', 't', 'a', 'r', 'o', 'l', 'c', 'd', 'g', 'd', 'd', 'g', 'y', 'b', 'v', 'f'],
            12: ['e', 'i', 'i', 'n', 's', 'a', 's', 'r', 'l', 'c', 'p', 'u', 'm', 'h', 'd', 'g', 'b', 'b', 'f'],
            13: ['i', 'e', 'n', 't', 'n', 'o', 'a', 'a', 'l', 'c', 'u', 'm', 'm', 'h', 'y', 'g', 'b', 'b', 'z'],
            14: ['i', 'e', 't', 's', 's', 'a', 'o', 'r', 'l', 'c', 'u', 'm', 'h', 'h', 'g', 'g', 'b', 'b', 'f'],
            15: ['i', 's', 't', 'n', 'n', 'o', 'o', 'r', 'l', 'c', 'u', 'm', 'h', 'd', 'g', 'y', 'b', 'f', 'f'],
            16: ['i', 's', 't', 's', 's', 'n', 'a', 'a', 'l', 'c', 'u', 'm', 'h', 'd', 'g', 'g', 'b', 'f', 'f'],
            17: ['i', 's', 'n', 'n', 'n', 'r', 'a', 'a', 'l', 'c', 'm', 'u', 'm', 'd', 'g', 'y', 'b', 'f', 'f'],
            18: ['i', 's', 's', 't', 't', 'n', 'r', 'a', 'l', 'c', 'm', 'u', 'm', 'd', 'g', 'y', 'b', 'f', 'f'],
            19: ['i', 'e', 'n', 's', 'n', 'a', 's', 'n', 'c', 'l', 'p', 'm', 'h', 'd', 'd', 'd', 'g', 'f', 'z'],
            20: ['i', 'o', 's', 'n', 's', 'r', 'a', 'n', 'c', 'l', 'p', 'h', 'm', 'h', 'd', 'g', 'y', 'b', 'f']
        }
        # if no letter chosen from above, pick a random one (extra weight on vowels)
        if guess_letter == '':
            length = len(word)
            letters = letters_table.get(length, [])
            for letter in letters:
                if letter not in self.guessed_letters:
                    return letter

        return guess_letter

fivegram = 0.24
fourgram = 0.22
trigram = 0.2
bigram = 0.18
unigram = 0.16
success_rate_list = []

def adjust_weights(success_rate, fivegram, fourgram, trigram, bigram, unigram, min_weight=0.01):
    if success_rate < 0.4:
        fivegram += 0.05
        fourgram += 0.05
        trigram += 0.05
        bigram -= 0.05
        unigram -= 0.05
    elif success_rate > 0.4 and success_rate < 0.5:
        fivegram += 0.025
        fourgram += 0.025
        trigram += 0.025
        bigram -= 0.025
        unigram += 0.025
    elif success_rate > 0.5 and success_rate < 0.55:
        fivegram += 0.01
        fourgram += 0.01
        trigram += 0.01
        bigram -= 0.01
        unigram -= 0.01
    elif success_rate > 0.55:
        fivegram += 0.005
        fourgram += 0.005
        trigram += 0.005
        bigram -= 0.005
        unigram -= 0.005
    
    fivegram = max(min_weight, fivegram)
    fourgram = max(min_weight, fourgram)
    trigram = max(min_weight, trigram)
    bigram = max(min_weight, bigram)
    unigram = max(min_weight, unigram)

    total_weight = fivegram + fourgram + trigram + bigram + unigram
    fivegram /= total_weight
    fourgram /= total_weight
    trigram /= total_weight
    bigram /= total_weight
    unigram /= total_weight
    
    return fivegram, fourgram, trigram, bigram, unigram