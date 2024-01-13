#include "ArgParser.h"
#include "Errors.h"

ArgumentParser::ArgParser::ArgParser(const std::string& description) {
    this->description = description;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::AddStringArgument(const std::string& name, const std::string& description) {
    Argument arg;

    arg.type = 's';
    arg.short_name = '\0';
    arg.long_name = name;
    arg.description = description;
    arg.is_flag = false;
    arg.is_positional = false;
    arg.is_multi_value = false;
    arg.is_default = false;
    arg.is_set = false;
    arg.min_count = 0;
    arg.max_count = 0;
    arg.value_storage = nullptr;
    arg.string_storage = nullptr;
    arg.values_storage = nullptr;
    arg.flag_storage = nullptr;

    arguments.push_back(arg);
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::AddStringArgument(char short_name, const std::string& name, const std::string& description) {
    Argument arg;

    arg.type = 's';
    arg.short_name = short_name;
    arg.long_name = name;
    arg.description = description;
    arg.is_flag = false;
    arg.is_positional = false;
    arg.is_multi_value = false;
    arg.is_default = false;
    arg.is_set = false;
    arg.min_count = 0;
    arg.max_count = 0;
    arg.value_storage = nullptr;
    arg.string_storage = nullptr;
    arg.values_storage = nullptr;
    arg.flag_storage = nullptr;

    arguments.push_back(arg);
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::AddIntArgument(const std::string& name, const std::string& description) {
    Argument arg;

    arg.type = 'i';
    arg.short_name = '\0';
    arg.long_name = name;
    arg.description = description;
    arg.is_flag = false;
    arg.is_positional = false;
    arg.is_multi_value = false;
    arg.is_default = false;
    arg.is_set = false;
    arg.min_count = 0;
    arg.max_count = 0;
    arg.value_storage = nullptr;
    arg.string_storage = nullptr;
    arg.values_storage = nullptr;
    arg.flag_storage = nullptr;

    arguments.push_back(arg);
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::AddIntArgument(char short_name, const std::string& name, const std::string& description) {
    Argument arg;

    arg.type = 'i';
    arg.short_name = short_name;
    arg.long_name = name;
    arg.description = description;
    arg.is_flag = false;
    arg.is_positional = false;
    arg.is_multi_value = false;
    arg.is_default = false;
    arg.is_set = false;
    arg.min_count = 0;
    arg.max_count = 0;
    arg.value_storage = nullptr;
    arg.string_storage = nullptr;
    arg.values_storage = nullptr;
    arg.flag_storage = nullptr;

    arguments.push_back(arg);
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::AddFlag(const std::string& name, const std::string& description) {
    Argument arg;

    arg.type = 'f';
    arg.short_name = '\0';
    arg.long_name = name;
    arg.description = description;
    arg.is_flag = true;
    arg.is_positional = false;
    arg.is_multi_value = false;
    arg.is_default = false;
    arg.is_set = false;
    arg.min_count = 0;
    arg.max_count = 0;
    arg.value_storage = nullptr;
    arg.string_storage = nullptr;
    arg.values_storage = nullptr;
    arg.flag_storage = nullptr;

    arguments.push_back(arg);
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::AddFlag(
        char short_name, const std::string& name, const std::string& description) {
    Argument arg;

    arg.type = 'f';
    arg.short_name = short_name;
    arg.long_name = name;
    arg.description = description;
    arg.is_flag = true;
    arg.is_positional = false;
    arg.is_multi_value = false;
    arg.is_default = false;
    arg.is_set = false;
    arg.min_count = 0;
    arg.max_count = 0;
    arg.value_storage = nullptr;
    arg.string_storage = nullptr;
    arg.values_storage = nullptr;
    arg.flag_storage = nullptr;

    arguments.push_back(arg);
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::MultiValue(int min_count, int max_count) {
    arguments.back().type = 'm';
    arguments.back().is_multi_value = true;
    arguments.back().min_count = min_count;
    arguments.back().max_count = max_count;
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::Positional() {
    arguments.back().is_positional = true;
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::Optional() {
    arguments.back().optional = true;
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::StoreValue(std::string& value) {
    arguments.back().string_storage = &value;
    arguments.back().externally_stored = true;
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::StoreValue(int& value) {
    arguments.back().value_storage = &value;
    arguments.back().externally_stored = true;
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::StoreValues(std::vector<std::string>& values) {
    arguments.back().values_storage = &values;
    arguments.back().externally_stored = true;
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::StoreValue(bool& value) {
    arguments.back().flag_storage = &value;
    arguments.back().externally_stored = true;
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::Default(const std::string& value) {
    arguments.back().is_default = true;
    arguments.back().string_storage = new std::string(value);
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::Default(int value) {
    arguments.back().is_default = true;
    arguments.back().value_storage = new int(value);
    return *this;
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::Default(bool value) {
    arguments.back().is_default = true;
    arguments.back().flag_storage = new bool(value);
    return *this;
}

bool ArgumentParser::ArgParser::PreParseCheck() {
    /*
     * pre-check: there must not be two arguments with the same name
     * and not more than one positional argument
     */
    for (int arg = 0; arg < arguments.size(); ++arg)
        for (int arg2 = arg + 1; arg2 < arguments.size(); ++arg2)
            if (arguments[arg].long_name == arguments[arg2].long_name)
                return DuplicateError(arguments[arg].long_name, HelpDescription());
    return true;
}

bool ArgumentParser::ArgParser::PostParseCheck() {
    /*
     * post-check: all not-optional, not-default and not-flag arguments must
     * be set or have default value and all multi value arguments must have
     * at least min_count values and not more than max_count values
     */
    for (int i = 0; i < arguments.size(); ++i) {
        if (!arguments[i].optional and !arguments[i].is_default and !arguments[i].is_set and !arguments[i].is_flag and !arguments[i].is_help)
            return NotFoundError(arguments[i].long_name, HelpDescription());
        if (arguments[i].is_multi_value and
            (arguments[i].values_storage->size() < arguments[i].min_count or arguments[i].values_storage->size() > arguments[i].max_count))
            return MultiValueError(arguments[i].long_name, HelpDescription());
    }
    return true;
}

bool ArgumentParser::ArgParser::Parse(const std::vector<std::string>& args) {
    if (!PreParseCheck())
        return false;

    /* set program name */
    program_name = args[0];

    std::vector<std::string> positional_args;
    /* skip program name */
    for (int i = 1; i < args.size(); ++i) {
        if (args[i][0] == '-') {
            if (args[i][1] == '-') {
                std::string raw_name = args[i].substr(2);
                std::string name, value;
                bool is_flag = false;
                bool found = false;

                /* if no = then flag */
                if (raw_name.find('=') == std::string::npos) {
                    is_flag = true;
                    name = raw_name;
                }
                else {
                    name = raw_name.substr(0, raw_name.find('='));
                    value = raw_name.substr(raw_name.find('=') + 1);
                }

                /* find argument by name */
                for (int j = 0; j < arguments.size() and !found; ++j) {
                    if (arguments[j].long_name == name) {
                        /* if argument is help, print help and exit */
                        /* HOOK: store memory for help flag or we will get SIGABRT */
                        if (arguments[j].is_help) {
                            arguments[j].flag_storage = new bool(true);
                            std::cout << HelpDescription() << '\n';
                            return true;
                        }
                        if (is_flag) {
                            if (arguments[j].flag_storage == nullptr) {
                                if (arguments[j].externally_stored)
                                    return StorageError(name, HelpDescription());
                                else
                                    arguments[j].flag_storage = new bool;
                            } /* storage */
                            arguments[j].is_set = true;
                            *arguments[j].flag_storage = true;
                        } /* flag */
                        else {
                            if (arguments[j].is_multi_value) {
                                /* multi value only for integers currently */
                                if (!arguments[j].is_set)
                                    arguments[j].is_set = true;
                                if (arguments[j].values_storage == nullptr) {
                                    if (arguments[j].externally_stored)
                                        return StorageError(name, HelpDescription());
                                    else
                                        arguments[j].values_storage = new std::vector<std::string>;
                                } /* storage */
                                arguments[j].values_storage->push_back(value);
                            } /* multi value */
                            else {
                                /* need to determine type */
                                if (arguments[j].type == 'i') {
                                    if (arguments[j].value_storage == nullptr) {
                                        if (arguments[j].externally_stored)
                                            return StorageError(name, HelpDescription());
                                        else
                                            arguments[j].value_storage = new int;
                                    } /* storage */
                                    *arguments[j].value_storage = std::stoi(value);
                                    arguments[j].is_set = true;
                                } /* int */
                                else if (arguments[j].type == 's') {
                                    if (arguments[j].string_storage == nullptr) {
                                        if (arguments[j].externally_stored)
                                            return StorageError(name, HelpDescription());
                                        else
                                            arguments[j].string_storage = new std::string;
                                    } /* storage */
                                    *arguments[j].string_storage = value;
                                    arguments[j].is_set = true;
                                } /* string */
                                else
                                    return TypeError(name, HelpDescription());
                            } /* single value */
                        } /* not flag */
                        found = true;
                    } /* found */
                } /* for */
                if (!found)
                    return NotFoundError(name, HelpDescription());
            } /* long name */
            else if (args[i].find('=') == std::string::npos) {
                /* short name */
                bool is_flag = false;
                if (args[i].size() > 2 or i == args.size() - 1 or args[i + 1][0] == '-')
                    is_flag = true;

                if (!is_flag) {
                    char short_name = args[i][1];
                    std::string value = args[i + 1];

                    /* find by short name */
                    bool found = false;
                    for (int j = 0; j < arguments.size() and !found; ++j) {
                        if (arguments[j].short_name == short_name) {
                            if (arguments[j].is_multi_value) {
                                /* multi value only for integers currently */
                                if (!arguments[j].is_set)
                                    arguments[j].is_set = true;
                                if (arguments[j].values_storage == nullptr) {
                                    if (arguments[j].externally_stored)
                                        return StorageError(arguments[j].long_name, HelpDescription());
                                    else
                                        arguments[j].values_storage = new std::vector<std::string>;
                                } /* storage */
                                arguments[j].values_storage->push_back(value);
                            } /* multi value */
                            else {
                                /* need to determine type */
                                if (arguments[j].type == 'i') {
                                    if (arguments[j].value_storage == nullptr) {
                                        if (arguments[j].externally_stored)
                                            return StorageError(arguments[j].long_name, HelpDescription());
                                        else
                                            arguments[j].value_storage = new int;
                                    } /* storage */
                                    *arguments[j].value_storage = std::stoi(value);
                                    arguments[j].is_set = true;
                                } /* int */
                                else if (arguments[j].type == 's') {
                                    if (arguments[j].string_storage == nullptr) {
                                        if (arguments[j].externally_stored)
                                            return StorageError(arguments[j].long_name, HelpDescription());
                                        else
                                            arguments[j].string_storage = new std::string;
                                    } /* storage */
                                    *arguments[j].string_storage = value;
                                    arguments[j].is_set = true;
                                } /* string */
                                else
                                    return TypeError(arguments[j].long_name, HelpDescription());
                            } /* single value */
                            found = true;
                        } /* found */
                    } /* for */
                    if (!found)
                        return NotFoundError(std::string(1, short_name) + " (short)", HelpDescription());
                    /* WARNING: if not flag found, need to increment i */
                    ++i;
                } /* not flag */
                else {
                    /* flags can be stored in one argument, for example -abc */
                    for (int k = 1; k < args[i].size(); ++k) {
                        char short_name = args[i][k];
                        bool found = false;
                        for (int j = 0; j < arguments.size() and !found; ++j) {
                            if (arguments[j].short_name == short_name) {
                                if (arguments[j].flag_storage == nullptr) {
                                    if (arguments[j].externally_stored)
                                        return StorageError(arguments[j].long_name, HelpDescription());
                                    else
                                        arguments[j].flag_storage = new bool;
                                } /* storage */
                                arguments[j].is_set = true;
                                *arguments[j].flag_storage = true;
                                found = true;
                            } /* found */
                        } /* for */
                        if (!found)
                            return NotFoundError(std::string(1, short_name) + " (short)", HelpDescription());
                    } /* for */
                } /* flag */
            } /* short name */
            else /* invalid short name */
                return InvalidShortNameError(args[i], HelpDescription());
        } /* argument */
        else {
            /* positional */
            positional_args.push_back(args[i]);
        }
    } /* main loop */

    /* store positional args */
    for (int i = arguments.size() - 1; i >= 0; --i) {
        if (arguments[i].is_positional) {
            /* if positional is multi-value too it will eat all positional args */
            if (arguments[i].is_multi_value) {
                if (!arguments[i].is_set)
                    arguments[i].is_set = true;
                if (arguments[i].values_storage == nullptr) {
                    if (arguments[i].externally_stored)
                        return StorageError(arguments[i].long_name, HelpDescription());
                    else
                        arguments[i].values_storage = new std::vector<std::string>;
                } /* storage */
                for (int j = 0; j < positional_args.size(); j++)
                    arguments[i].values_storage->push_back(positional_args.at(j));
                /* we done with all arguments, drop vector and break */
                positional_args.clear();
                break;
            }
            /* determine type and set */
            if (arguments[i].type == 'i') {
                if (arguments[i].value_storage == nullptr) {
                    if (arguments[i].externally_stored)
                        return StorageError(arguments[i].long_name, HelpDescription());
                    else
                        arguments[i].value_storage = new int;
                } /* storage */
                if (positional_args.empty())
                    return NotFoundError(arguments[i].long_name, HelpDescription());
                *arguments[i].value_storage = std::stoi(positional_args.back());
                positional_args.pop_back();
                arguments[i].is_set = true;
            } /* int */
            else if (arguments[i].type == 's') {
                if (arguments[i].string_storage == nullptr) {
                    if (arguments[i].externally_stored)
                        return StorageError(arguments[i].long_name, HelpDescription());
                    else
                        arguments[i].string_storage = new std::string;
                } /* storage */
                if (positional_args.empty())
                    return NotFoundError(arguments[i].long_name, HelpDescription());
                *arguments[i].string_storage = positional_args.back();
                positional_args.pop_back();
                arguments[i].is_set = true;
            } /* string */
            else
                return TypeError(arguments[i].long_name, HelpDescription());
        } /* positional */
    } /* positional loop */
    if (!positional_args.empty())
        return UnknownArgumentError(positional_args.back(), HelpDescription());

    if (!PostParseCheck())
        return false;
    return true;
}

bool ArgumentParser::ArgParser::Parse(int argc, char** argv) {
    std::vector<std::string> args;
    for (int i = 0; i < argc; ++i)
        args.push_back(argv[i]);
    return Parse(args);
}

bool ArgumentParser::ArgParser::Help() {
    return !help_message.empty();
}

ArgumentParser::ArgParser& ArgumentParser::ArgParser::AddHelp(char short_name, const std::string &name, const std::string &help_message) {
    this->AddStringArgument(short_name, name);
    arguments.back().is_help = true;
    this->help_message += this->description + '\n';
    this->help_message += help_message + "\n\n";
    return *this;
}

std::string ArgumentParser::ArgParser::HelpDescription() {
    std::string help = this->help_message;

    help += "Usage: " + program_name + " [options] \n";
    for (int i = 0; i < arguments.size(); ++i) {
        std::string arg_desc;
        std::string arg_value;

        if (arguments[i].type == 'i')
            arg_value = "=<int>";
        else if (arguments[i].type == 's')
            arg_value = "=<string>";
        else if (arguments[i].type == 'm')
            arg_value = "=<int> ...";
        else
            arg_value = "";

        if (arguments[i].is_positional)
            arg_desc = arguments[i].long_name + '\t' + arguments[i].description;
        else if (arguments[i].short_name != '\0')
            arg_desc = "\t-" + std::string(1, arguments[i].short_name) + ",\t--" + arguments[i].long_name + arg_value + ",\t" + arguments[i].description;
        else
            arg_desc = "\t--" + arguments[i].long_name + arg_value + ",\t" + arguments[i].description;
        arg_desc += '\n';

        help += arg_desc;
    }
    return help;
}

bool ArgumentParser::ArgParser::GetFlag(const std::string& name) {
    for (int i = 0; i < arguments.size(); ++i)
        if (arguments[i].long_name == name)
            return arguments[i].flag_storage != nullptr && *arguments[i].flag_storage;
    return false;
}

std::string ArgumentParser::ArgParser::GetStringValue(const std::string& name) {
    for (int i = 0; i < arguments.size(); ++i)
        if (arguments[i].long_name == name)
            return arguments[i].string_storage == nullptr ? "" : *arguments[i].string_storage;
    return "";
}

int ArgumentParser::ArgParser::GetIntValue(const std::string& name) {
    for (int i = 0; i < arguments.size(); ++i)
        if (arguments[i].long_name == name)
            return arguments[i].value_storage == nullptr ? 0 : *arguments[i].value_storage;
    return 0;
}

std::string ArgumentParser::ArgParser::GetStringValue(const std::string& name, int index) {
    for (int i = 0; i < arguments.size(); ++i)
        if (arguments[i].long_name == name)
            return arguments[i].values_storage != nullptr and index < arguments[i].values_storage->size() ? arguments[i].values_storage->at(index) : "";
    return 0;
}
