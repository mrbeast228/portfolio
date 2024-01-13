#pragma once
#include <fstream>
#include <cstring>
#include <vector>

typedef unsigned char byte;

class BinaryFile {
private:
    byte* buffer = nullptr;
    size_t size = 0;

    static bool get_bit(byte* buffer, size_t pos);

    static void set_bit(byte* buffer, size_t pos, bool value);

    void count_service_bits(byte* b, size_t size, bool zeroing = false);

public:
    std::string filename;
    size_t service_bits = -1; /* not set */
    size_t original_size = -1; /* not set */

    BinaryFile() {}

    BinaryFile(byte* src, size_t size);

    BinaryFile(const std::string& filename);

    BinaryFile(std::fstream& archive);

    ~BinaryFile() = default;

    byte* getBuffer();

    size_t getSize();

    void HammingEncode();

    void HammingDecode();

    void write();

    void write(std::fstream& archive);
};

const byte header[] = {0xB1, 0xBA, 0xB0, 0xBA, 0xFF};

bool CheckHeader(std::fstream& archive) {
    byte* buffer = new byte[sizeof(header)];
    archive.read((char*)buffer, sizeof(header));
    bool result = std::memcmp(buffer, header, sizeof(header)) == 0;
    delete[] buffer;
    return result;
}

class Archiver {
private:
    size_t count_of_files = 0;
    std::string archive_filename;
    std::fstream archive;
    std::vector<BinaryFile> files;

    void regenerate_archive();

    void restore_from_archive();

public:
    Archiver(const std::string& arc_filename);

    ~Archiver();

    bool is_empty() const;

    size_t check_file_is_in_archive(const std::string& filename);

    std::vector<std::string> list_files();

    void add_files(const std::vector<std::string>& filenames);

    void remove_files(const std::vector<std::string>& filenames);

    void merge_archives(const std::string& arc_filename);

    void extract_files(const std::vector<std::string>& filenames);
};
