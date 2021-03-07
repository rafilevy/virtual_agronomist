class TimingTranslator:
    def __init__(self, crops_timing_lists):             # use TimingInfoCreator to read and customise translation table
        self.crops_timing_lists = crops_timing_lists    # then pass the data to the translator.
        print("Made Translator")

    def standardise_name(self,crop_name,timing):
        if crop_name not in self.crops_timing_lists.keys():
            print("Crop name not known. Known crops: ")
            for key in self.crops_timing_lists:
                print("* " + key)
            return
        for ls in self.crops_timing_lists[crop_name]:
            if timing in ls:
                return ls[0]
        print("Timing not translatable")

    def get_possible_crops(self, timing):
        possible_crops = set()
        for key in self.crops_timing_lists:
            for ls in self.crops_timing_lists[key]:
                if timing in ls:
                    possible_crops.add(key)
        return possible_crops

    def translate(self, text, crop):
        print(type(self.crops_timing_lists))
        if crop in self.crops_timing_lists.keys():
            for timing in self.crops_timing_lists[crop]:
                for name in timing:
                    if name in text and not name == timing[0]:
                        text = text.replace(name, timing[0])
        return text

    def contains_translatable_timing(self,text):
        for crop in self.crops_timing_lists.keys():
            for timing in self.crops_timing_lists[crop]:
                for name in timing:
                    if name in text and not name == timing[0]:
                        return True
        return False


class TimingInfoCreator:
    def __init__(self, data):
        print("made info creator")
        self.crops_timing_data = data       # a dict of crop name : list of lists of equivalent timing terms

    def read_csv_translate_table(self, filename):
        self.crops_timing_data = {}
        import  csv
        csv.register_dialect('csv_dialect', skipinitialspace=True)

        with open(filename) as f:
            reader = csv.reader(f, dialect='csv_dialect')
            data = list(reader)

        crop_name_line = True
        crop_name = ""
        for line in data:
            if not line:
                crop_name = ""
                crop_name_line = True
            elif crop_name_line:
                crop_name = line[0].lower()
                self.add_crop(crop_name)
                crop_name_line = False
            else:
                self.add_standard_timing(crop_name, line[0].lower())
                for tr in line[1:]:
                    self.add_translatable_timing(crop_name, line[0].lower(), tr.lower())

    def add_crop(self, crop_name):
        crop_name = crop_name.lower()
        if crop_name in self.crops_timing_data.keys():
            print("This crop is already in the data")
            return
        self.crops_timing_data[crop_name] = []

    def add_standard_timing(self,crop_name, standard_timing):
        crop_name = crop_name.lower()
        standard_timing = standard_timing.lower()
        #  print(self.crops_timing_data)
        if crop_name not in self.crops_timing_data.keys():
            print("Crop not known")
            return

        if self.crops_timing_data[crop_name] == []:
            self.crops_timing_data[crop_name] = [[standard_timing]]
        else:
            self.crops_timing_data[crop_name].append([standard_timing])

    def add_translatable_timing(self, crop_name, standard_timing, translate_timing):
        crop_name = crop_name.lower()
        standard_timing = standard_timing.lower()
        translate_timing = translate_timing.lower()
        if crop_name not in self.crops_timing_data.keys():
            print("Crop not known")
            return

        for timings in self.crops_timing_data[crop_name]:
            if standard_timing in timings:
                if translate_timing not in timings:
                    timings.append(translate_timing)
                    return
                else:
                    print("this translation is already in the data")
                    return

        print("Standard timing not known")

    def get_data(self):
        return self.crops_timing_data
