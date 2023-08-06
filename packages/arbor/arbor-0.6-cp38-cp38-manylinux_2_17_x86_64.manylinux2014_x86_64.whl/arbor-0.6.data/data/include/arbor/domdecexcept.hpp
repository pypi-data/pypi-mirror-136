#pragma once

#include <string>

#include <arbor/arbexcept.hpp>
#include <arbor/domain_decomposition.hpp>

namespace arb {
struct dom_dec_exception: public arbor_exception {
    dom_dec_exception(const std::string& what): arbor_exception("Invalid domain decomposition: " + what) {}
};

struct invalid_gj_cell_group: dom_dec_exception {
    invalid_gj_cell_group(cell_gid_type gid_0, cell_gid_type gid_1);
    cell_gid_type gid_0, gid_1;
};

struct invalid_sum_local_cells: dom_dec_exception {
    invalid_sum_local_cells(unsigned gc_wrong, unsigned gc_right);
    unsigned gc_wrong, gc_right;
};

struct duplicate_gid: dom_dec_exception {
    duplicate_gid(cell_gid_type gid);
    cell_gid_type gid;
};

struct out_of_bounds: dom_dec_exception {
    out_of_bounds(cell_gid_type gid, unsigned num_cells);
    cell_gid_type gid;
    unsigned num_cells;
};

struct invalid_backend: dom_dec_exception {
    invalid_backend(int rank);
    int rank;
};

struct incompatible_backend: dom_dec_exception {
    incompatible_backend(int rank, cell_kind kind);
    int rank;
    cell_kind kind;
};
} // namespace arb

