#include <cmath>
#include "Library.h"

/* basic operations */
BinaryFile::BinaryFile(byte *src, size_t size) {
    buffer = new byte[size];
    std::memcpy(buffer, src, size);
    this->size = size;
}

BinaryFile::BinaryFile(const std::string &filename) {
    this->filename = filename;

    std::ifstream file(filename, std::ios::binary | std::ios::ate);
    if (not file.is_open())
        throw std::runtime_error("Cannot open file " + filename);

    size = file.tellg();
    buffer = new byte[size];
    file.seekg(0, std::ios::beg);
    file.read((char *) buffer, size);
    file.close();
}

BinaryFile::BinaryFile(std::fstream& archive) {
    /* read filename */
    size_t filename_length;
    archive.read((char*)&filename_length, sizeof(filename_length));
    char* filename = new char[filename_length + 1];
    archive.read(filename, filename_length);
    filename[filename_length] = '\0';
    this->filename = filename;
    delete[] filename;

    /* read file */
    size_t file_length, original_size, service_bits;
    archive.read((char*)&file_length, sizeof(file_length));
    archive.read((char*)&original_size, sizeof(original_size));
    archive.read((char*)&service_bits, sizeof(service_bits));

    buffer = new byte[file_length];
    archive.read((char*)buffer, file_length);
    size = file_length;
    this->original_size = original_size;
    this->service_bits = service_bits;
}

byte *BinaryFile::getBuffer() {
    return buffer;
}

size_t BinaryFile::getSize() {
    return size;
}


/* service bits operations */
bool BinaryFile::get_bit(byte* buffer, size_t pos) {
    return (buffer[pos / 8] >> (7 - pos % 8)) & 1;
}

void BinaryFile::set_bit(byte* buffer, size_t pos, bool value) {
    if (value)
        buffer[pos / 8] |= 1 << (7 - pos % 8);
    else
        buffer[pos / 8] &= ~(1 << (7 - pos % 8));
}


/* hamming code operations */
void BinaryFile::count_service_bits(byte* b, size_t size, bool zeroing) {
    /* works on already reallocated buffer */
    for (size_t i = 0; i < service_bits; i++) {
        int sum = 0;
        for (size_t j = 0; j < size * 8; j++)
            if ((j + 1) & (1 << i))
                sum += get_bit(b, j);
        set_bit(b, (1 << i) - 1, !zeroing && (sum % 2 == 0));
    }
}

void BinaryFile::HammingEncode() {
    /* count service bits */
    service_bits = 0;
    while ((1 << service_bits) < size * 8 + service_bits + 1)
        service_bits++;

    /* allocate memory for encoded data */
    size_t new_size = (size * 8 + service_bits + 7) / 8;
    size_t new_bufsize = (size * 8 + service_bits + 8) / 8;
    byte* new_buffer = new byte[new_bufsize];

    /* set zeros by default */
    std::memset(new_buffer, 0, new_bufsize);

    /* place bits */
    size_t pos = 0;
    for (size_t i = 0; i < new_size * 8; i++) {
        if ((i & (i + 1)) == 0) {
            set_bit(new_buffer, i, false);
            continue;
        }
        set_bit(new_buffer, i, get_bit(buffer, pos++));
    }

    /* count service bits */
    count_service_bits(new_buffer, new_size);

    /* count last parity bit */
    int sum = 0;
    for (size_t i = 0; i < new_size * 8; i++)
        sum += get_bit(new_buffer, i);
    set_bit(new_buffer, new_size * 8, sum % 2 == 0);

    /* replace buffer */
    delete[] buffer;
    buffer = new_buffer;
    original_size = size;
    size = new_bufsize;
}

void BinaryFile::HammingDecode() {
    /* recount service bits on copy of buffer */
    byte* copy = new byte[size];
    std::memcpy(copy, buffer, size);
    size_t size74 = (original_size * 8 + service_bits + 7) / 8;
    /* zeroing control bits is necessary! */
    count_service_bits(copy, size74, true);
    count_service_bits(copy, size74);

    /* find error position */
    size_t error_pos = 0;
    for (size_t i = 0; i < size74 * 8; i++)
        if (get_bit(copy, i) != get_bit(buffer, i))
            error_pos += i + 1;

    /* check last parity bit */
    int sum = 0;
    bool parity_error = false;
    for (size_t i = 0; i < size74 * 8; i++)
        sum += get_bit(buffer, i);
    if ((sum % 2 == 0) != get_bit(buffer, size74 * 8))
        parity_error = true;

    /* fix error */
    if (parity_error && error_pos)
        set_bit(buffer, error_pos - 1, not get_bit(buffer, error_pos - 1));
    /* detect double error */
    else if (!parity_error && error_pos)
        throw std::runtime_error("Double error detected!");

    /* drop copy */
    delete[] copy;

    /* restore original data */
    byte* restored = new byte[original_size];
    size_t pos = 0;
    for (size_t i = 0; i < size * 8; i++) {
        if ((i & (i + 1)) == 0)
            continue;
        set_bit(restored, pos++, get_bit(buffer, i));
    }

    /* replace buffer */
    delete[] buffer;
    buffer = restored;
    size = original_size;
    original_size = -1;
    service_bits = -1;
}

void BinaryFile::write() {
    /* check file name */
    if (filename.empty() or filename.length() > 255)
        throw std::runtime_error("Invalid filename! Maybe file is virtual or developer is stupid?");

    /* open file */
    std::ofstream file(filename, std::ios::binary);
    if (not file.is_open())
        throw std::runtime_error("Cannot open file " + filename);

    file.write((char*)buffer, size);
    file.close();
}

void BinaryFile::write(std::fstream& archive) {
    /* check file name */
    if (filename.empty() or filename.length() > 255)
        throw std::runtime_error("Invalid filename! Maybe file is virtual or developer is stupid?");

    /* write filename */
    size_t filename_length = filename.length();
    archive.write((char*)&filename_length, sizeof(filename_length));
    archive.write((char*)filename.c_str(), filename_length);

    /* write file */
    size_t file_length = size;
    archive.write((char*)&file_length, sizeof(file_length));
    archive.write((char*)&original_size, sizeof(original_size));
    archive.write((char*)&service_bits, sizeof(service_bits));
    archive.write((char*)buffer, file_length);
}