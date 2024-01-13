#pragma once
#include <climits>
#include "Argument.h"

#define TODO() ((void)0) /* TODO empty pseudo-function */

namespace ArgumentParser {
    class ArgParser {
    private:
        std::string program_name;
        std::string description;
        std::vector<Argument> arguments;
        std::string help_message;

    public:
        ArgParser(const std::string& description);

        ArgParser& AddStringArgument(const std::string& name, const std::string& description = "");
        ArgParser& AddStringArgument(char short_name, const std::string& name, const std::string& description = "");
        ArgParser& AddIntArgument(const std::string& name, const std::string& description = "");
        ArgParser& AddIntArgument(char short_name, const std::string& name, const std::string& description = "");
        ArgParser& AddFlag(const std::string& name, const std::string& description = "");
        ArgParser& AddFlag(char short_name, const std::string& name, const std::string& description = "");

        ArgParser& MultiValue(int min_count = 0, int max_count = INT_MAX);
        ArgParser& Positional();
        ArgParser& Optional();

        ArgParser& StoreValue(std::string& value);
        ArgParser& StoreValue(int& value);
        ArgParser& StoreValues(std::vector<std::string>& values);
        ArgParser& StoreValue(bool& value);

        bool SetValue(Argument& argument, const std::string& value);

        bool Parse(const std::vector<std::string>& args);
        bool Parse(int argc, char** argv);

        bool Help();
        std::string HelpDescription();

        bool GetFlag(const std::string& name);
        std::string GetStringValue(const std::string& name);
        int GetIntValue(const std::string& name);
        std::string GetStringValue(const std::string& name, int index);

        ArgParser& AddHelp(char short_name, const std::string& name, const std::string& description);
        ArgParser& Default(const std::string& value);
        ArgParser& Default(int value);
        ArgParser& Default(bool value);

        bool PreParseCheck();
        bool PostParseCheck();
    }; /* parser */
} /* namespace */
