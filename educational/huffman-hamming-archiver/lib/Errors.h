#ifndef LABWORK4_SPBUPOS_ERRORS_H
#define LABWORK4_SPBUPOS_ERRORS_H

#include <iostream>

bool StorageError(const std::string& name, const std::string& help_message) {
    std::cout << "ERROR: can't store " << name << ": no storage" << '\n';
    std::cout << help_message << '\n';
    return false;
}

bool NotFoundError(const std::string& name, const std::string& help_message) {
    std::cout << "ERROR: argument " << name << " not found" << '\n';
    std::cout << help_message << '\n';
    return false;
}

bool DuplicateError(const std::string& name, const std::string& help_message) {
    std::cout << "ERROR: duplicate argument " << name << '\n';
    std::cout << help_message << '\n';
    return false;
}

bool TypeError(const std::string& name, const std::string& help_message) {
    std::cout << "ERROR: wrong type for argument " << name << '\n';
    std::cout << help_message << '\n';
    return false;
}

bool InvalidShortNameError(const std::string& short_name, const std::string& help_message) {
    std::cout << "ERROR: invalid short name " << short_name << '\n';
    std::cout << help_message << '\n';
    return false;
}

bool UnknownArgumentError(const std::string& name, const std::string& help_message) {
    std::cout << "ERROR: unknown argument " << name << '\n';
    std::cout << help_message << '\n';
    return false;
}

bool MultiValueError(const std::string& name, const std::string& help_message) {
    std::cout << "ERROR: argument " << name << " out of range" << '\n';
    std::cout << help_message << '\n';
    return false;
}

#endif /* LABWORK4_SPBUPOS_ERRORS_H */
