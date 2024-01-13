#include <iostream>
#include "lib/Library.h"
#include "lib/ArgParser.h"

using namespace ArgumentParser;

std::ostream& operator<<(std::ostream& out, const std::vector<std::string>& vector) {
    for (const auto& item : vector)
        out << item << '\n';
    return out;
}

int main(int argc, char** argv) {
    try {
        std::vector<std::string> positional_arguments;
        auto parser = ArgParser("Hamming Archiver v1.0");

        parser.AddFlag('c', "create", "Create archive");
        parser.AddFlag('l', "list", "List files in archive");
        parser.AddFlag('a', "append", "Add files to archive");
        parser.AddFlag('x', "extract", "Extract files from archive");
        parser.AddFlag('d', "delete", "Delete files from archive");
        parser.AddFlag('A', "concatenate", "Concatenate two archives");

        parser.AddStringArgument('f', "file", "Archive filename");
        parser.AddHelp('h', "help", "This utility creates archive from files or extracts files from archive");
        parser.AddStringArgument("positional_arguments").MultiValue().Positional().StoreValues(positional_arguments);

        if (not parser.Parse(argc, argv)) {
            std::cout << "Cannot parse arguments!\n";
            return 1;
        }

        Archiver archiver(parser.GetStringValue("file"));

        if (parser.GetFlag("list")) {
            std::cout << archiver.list_files();
        } else if (parser.GetFlag("create")) {
            if (not archiver.is_empty())
                throw std::runtime_error("Archive is already exists!");
            archiver.add_files(positional_arguments);
        } else if (parser.GetFlag("append")) {
            archiver.add_files(positional_arguments);
        } else if (parser.GetFlag("extract")) {
            archiver.extract_files(positional_arguments);
        } else if (parser.GetFlag("delete")) {
            archiver.remove_files(positional_arguments);
        } else if (parser.GetFlag("concatenate")) {
            archiver.merge_archives(positional_arguments[0]);
        } else {
            std::cout << parser.HelpDescription() << '\n';
        }
        return 0;
    } catch (std::exception& e) {
        std::cout << e.what() << '\n';
        return 2;
    }
}
