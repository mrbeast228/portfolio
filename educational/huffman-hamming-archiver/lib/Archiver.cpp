#include "Library.h"

void Archiver::regenerate_archive() {
    /* open only if still not opened */
    if (not archive.is_open())
        archive.open(archive_filename, std::ios::out | std::ios::binary);
    if (not archive.is_open())
        throw std::runtime_error("Cannot open file " + archive_filename);

    /* write header */
    archive.write((char*)header, sizeof(header));

    /* write count of files */
    archive.write((char*)&count_of_files, sizeof(count_of_files));

    /* write is method of BinaryFile class */
    for (size_t i = 0; i < count_of_files; i++)
        files[i].write(archive);

    archive.close();
}

void Archiver::restore_from_archive() {
    /* archive already opened and header read! */
    /* read count of files */
    archive.read((char*)&count_of_files, sizeof(count_of_files));

    /* for each file read length of filename, filename, length of file, original_size of file, count of service bits, file */
    for (size_t i = 0; i < count_of_files; i++)
        files.emplace_back(archive);

    archive.close();
}

Archiver::Archiver(const std::string &arc_filename) {
    /* check file existence */
    archive_filename = arc_filename;
    archive.open(arc_filename, std::ios::in | std::ios::binary);
    if (archive.is_open()) { /* unpack */
        if (not CheckHeader(archive))
            throw std::runtime_error("Invalid archive!");
        restore_from_archive();
    }
}

Archiver::~Archiver() {
    if (archive.is_open())
        archive.close();
}

bool Archiver::is_empty() const {
    return count_of_files == 0;
}

size_t Archiver::check_file_is_in_archive(const std::string &filename) {
    for (size_t i = 0; i < count_of_files; i++)
        if (files[i].filename == filename)
            return i;
    return -1;
}

std::vector<std::string> Archiver::list_files() {
    std::vector<std::string> filenames;
    for (size_t i = 0; i < count_of_files; i++)
        filenames.push_back(files[i].filename);
    return filenames;
}

void Archiver::add_files(const std::vector<std::string> &filenames) {
    for (auto& filename : filenames) {
        if (check_file_is_in_archive(filename) != -1)
            throw std::runtime_error("File " + filename + " already in archive!");
        auto file = BinaryFile(filename);
        file.HammingEncode();
        files.emplace_back(file);
        count_of_files++;
    }
    regenerate_archive();
}

void Archiver::remove_files(const std::vector<std::string> &filenames) {
    for (auto& filename : filenames) {
        size_t index = check_file_is_in_archive(filename);
        if (index == -1)
            throw std::runtime_error("File " + filename + " not in archive!");
        files.erase(files.begin() + index);
        count_of_files--;
    }
    regenerate_archive();
}

void Archiver::merge_archives(const std::string &arc_filename) {
    Archiver arc(arc_filename);
    for (auto& file : arc.files) {
        if (check_file_is_in_archive(file.filename) != -1)
            throw std::runtime_error("File " + file.filename + " already in archive!");
        files.push_back(file);
        count_of_files++;
    }
    regenerate_archive();
}

void Archiver::extract_files(const std::vector<std::string> &filenames) {
    /* if archive empty - throw exception */
    if (count_of_files == 0)
        throw std::runtime_error("Archive is empty!");

    /* if list empty - extract all */
    if (filenames.empty()) {
        for (auto& file : files) {
            file.HammingDecode();
            file.write();
        }
        return;
    }
    for (auto& filename : filenames) {
        size_t index = check_file_is_in_archive(filename);
        if (index == -1)
            throw std::runtime_error("File " + filename + " not in archive!");
        files[index].HammingDecode();
        files[index].write();
    }
}
