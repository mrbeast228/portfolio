#ifndef LABWORK4_SPBUPOS_ARGUMENT_H
#define LABWORK4_SPBUPOS_ARGUMENT_H

#include <string>
#include <vector>

namespace ArgumentParser {
    class Argument {
    public:
        char type; /* i - int, s - string, f - flag, m - multi value */
        char short_name;
        std::string long_name;
        std::string description;
        bool is_flag;
        bool is_positional;
        bool is_multi_value;
        bool is_default;
        bool is_set;
        int min_count;
        int max_count;
        int* value_storage;
        std::string* string_storage;
        std::vector<std::string>* values_storage;
        bool* flag_storage;
        bool externally_stored = false;
        bool optional = false;
        bool is_help = false;

        ~Argument() {
            if (!externally_stored and is_set) {
                switch (type) {
                    case 'i':
                        delete value_storage;
                        break;
                    case 's':
                        delete string_storage;
                        break;
                    case 'm':
                        delete values_storage;
                        break;
                    case 'f':
                        delete flag_storage;
                        break;
                } /* switch */
            } /* if */
        } /* destructor */
    }; /* argument */
} /* namespace */

#endif /* LABWORK4_SPBUPOS_ARGUMENT_H */
