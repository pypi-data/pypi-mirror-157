import random
import string


class RandomChararcterGenerator:
    def __init__(self, num_char=0, which_kind=0, iter_num=0, iter_type=0):
        self.num_char = num_char
        self.which_kind = which_kind
        self.iter_num = iter_num
        self.iter_type = iter_type

    def coll_main(self):
        list_of_rands = []
        tuple_of_rands = ()
        dict_of_rands = {}
        set_of_rands = set()

        # ==========================

        if self.iter_type == 1:
            print('\nPut into list form:')
            for each_li_item in range(int(self.iter_num)):
                each_li_item = self.type_of_chars()
                list_of_rands.append(each_li_item)
            print(list_of_rands)

        # ==========================

        if int(self.iter_type) == 2:
            print('\nPut into tuple form')
            temp_list = []
            for each_to_tup in range(int(self.iter_num)):
                each_to_tup = self.type_of_chars()
                temp_list.append(each_to_tup)
            tuple_of_rands = tuple(temp_list)
            print(tuple_of_rands)

        # ==========================

        if int(self.iter_type) == 3:
            print('\nPut into dictionary form')
            temp_list_keys = []
            temp_list_vals = []
            for each_dic_it in range(int(self.iter_num)):
                each_dic_key = self.type_of_chars()
                temp_list_keys.append(each_dic_key)
            for each_dict_val in range(int(self.iter_num)):
                each_dict_val = self.type_of_chars()
                temp_list_vals.append(each_dict_val)
            from_zip = zip(temp_list_keys, temp_list_vals)
            conv_to_dic = dict(from_zip)
            dict_of_rands = conv_to_dic
            print(dict_of_rands)

        # ==========================

        if int(self.iter_type) == 4:
            print('\nPut into set form')
            for each_set_val in range(int(self.iter_num)):
                each_set_val = self.type_of_chars()
                set_of_rands.add(each_set_val)
            print(set_of_rands)

    # ==========================

    def type_of_chars(self):
        if self.which_kind == 1:
            x = self.just_uppers()
            return x
        if self.which_kind == 2:
            x = self.get_random_lower_case()
            return x
        if self.which_kind == 3:
            x = self.uppers_lowers()
            return x
        if self.which_kind == 4:
            x = self.just_numbers()
            return x
        if self.which_kind == 5:
            x = self.just_punctuation()
            return x
        if self.which_kind == 6:
            x = self.mix_of_all()
            return x

    # ==========================

    def just_uppers(self):
        characters = string.ascii_uppercase
        result_str = ''.join(random.choice(characters)
                             for i in range(self.num_char))
        print(result_str)
        return result_str

    # ==========================

    def get_random_lower_case(self):
        characters = string.ascii_lowercase
        result_str = ''.join(random.choice(characters)
                             for i in range(self.num_char))
        print(result_str)
        return result_str

    # ==========================

    def uppers_lowers(self):
        characters = string.ascii_letters
        result_str = ''.join(random.choice(characters)
                             for i in range(self.num_char))
        print(result_str)
        return result_str

    # ==========================

    def just_numbers(self):
        characters = string.digits
        result_str = ''.join(random.choice(characters)
                             for i in range(self.num_char))
        print(result_str)
        return result_str

    # ==========================

    def just_punctuation(self):
        characters = string.punctuation
        result_str = ''.join(random.choice(characters)
                             for i in range(self.num_char))
        print(result_str)
        return result_str

    # ==========================

    def mix_of_all(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        result_str = ''.join(random.choice(characters)
                             for i in range(self.num_char))
        print(result_str)
        return result_str


input_char = input('How many characters long? ')
print('What kind of characters do you want to use in the collection?\n'
      'You have the following patterns to pick from:\n'
      '1 - for all uppercase\n'
      '2 - for all lowercase\n'
      '3 - for a mix of upper and lowercase\n'
      '4 - for a mix of numbers\n'
      '5 - for a mix of punctuation\n'
      '6 - for a mix of everything\n')
mix_of_chars = input('Which would you like to use?')
iter_times = input('How many iterations? ')
print('What kind of collection would you like to create?\n'
      'Your options are:\n'
      '1. Lists\n'
      '2. Tuples (Immutable lists)\n'
      '3. Dictionaries (needs two values)\n'
      '4. Sets (Ordered lists)')
data_type = input('Type from the above: \n')

first_try = RandomChararcterGenerator(int(input_char), int(mix_of_chars),
                                      int(iter_times), int(data_type))

first_try.coll_main()

