/*!
* Wraps a triangle geometry for the needs of Eigen::KdBVH
* @author Maxime Lemonnier
*/

#pragma once

#include <Eigen/Dense>
#include <vector>
#include <array>
#include <numeric>
namespace Eigen
{

template <typename Index, typename Scalar, size_t _ShapeDim, size_t _Dim>
class BVHWrapper
{
public:
        static constexpr size_t Dim = _Dim;
        static constexpr size_t ShapeDim = _ShapeDim;
        typedef AlignedBox<Scalar, Dim> Box;
        typedef Matrix<Scalar, 1, Dim> Point;
        typedef Matrix<Index, 1, ShapeDim> ShapeIndices;
        typedef Matrix<Scalar, Dynamic, Dim, RowMajor> Points;
        typedef Matrix<Index, Dynamic, ShapeDim, RowMajor> StaticShapeMatrix;
        typedef Matrix<Index, Dynamic, Dynamic, RowMajor>  DynamicShapeMatrix;
        typedef typename std::conditional< (ShapeDim > 1), StaticShapeMatrix, DynamicShapeMatrix >::type Indices;
        typedef std::vector<Box> Boxes;
        typedef std::vector<size_t> Objects;
        BVHWrapper(Index * indices, size_t n_indices, Scalar * scalars, size_t n_points) :
            _indices(indices, int(n_indices), int(ShapeDim)), _points(scalars, int(n_points), int(Dim))
        {
            init();
        }

        BVHWrapper(const Ref<const Indices> indices, const Ref<const Points> points) :
            _indices(indices.data(), indices.rows(), indices.cols()), _points(points.data(), points.rows(), points.cols())
        {
            init();
        }

        void init()
        {
            size_t n_objects = _indices.rows();
            _boxes.reserve(n_objects);
            for(size_t i = 0; i < n_objects; i++)
            {
                AlignedBox<Scalar, Dim> box;
                
                for(size_t j = 0; j < ShapeDim; j++)
                    box.extend(_points.row(_indices(i, j)).transpose());

                _boxes.emplace_back(box);
            }

            _objects.resize(n_objects);
            std::iota(_objects.begin(), _objects.end(), 0u);
        }
        decltype(auto) point(Index i) const {return _points.row(i);}
        decltype(auto) indices(Index i) const {return _indices.row(i);}
        decltype(auto) begin() const { return _objects.cbegin();}
        decltype(auto) end() const { return _objects.cend();}
        decltype(auto) boxes_begin() const { return _boxes.cbegin();}
        decltype(auto) boxes_end() const { return _boxes.cend();}
        size_t n_objects() const {return _objects.size();}
        size_t n_points() const {return _points.rows();}

private:
        Map<const Indices> _indices;
        Map<const Points> _points;
        Boxes _boxes;
        Objects _objects;
};

}