/*!
* Wraps a triangle geometry for the needs of Eigen::KdBVH
* @author Maxime Lemonnier
*/

#pragma once

#include "traits.h"
#include <Eigen/Dense>
#include "line_intersections.h"
#include "line_distances.h"
#include <vector>
#include <array>
#include <numeric>
namespace Eigen
{

template <typename BVH, typename BVHWrapper>
struct RayTrianglesQuery
{
        static constexpr size_t Dim = BVHWrapper::Dim;
        typedef typename BVHWrapper::Point Point;
        typedef typename BVHWrapper::ShapeIndices Triangle;
        typedef scalar_t<Point> Scalar;

        struct Intersection
        {
                typename BVH::Object id;
                Point tuv;
        };
        struct Minimum
        {
                typename BVH::Object id;
                Scalar distance;
                Point tuv;
        };
        typedef std::vector<Intersection> Intersections;

        const std::vector<Intersection> & sorted()
        {
            std::sort(intersections.begin(), intersections.end(), [](const auto & lhs, const auto & rhs){return lhs.tuv[0] < rhs.tuv[0];});
            return intersections;
        }

        const BVHWrapper & wrapper;
        const Point origin;
        const Point direction;
        Point inv_direction;
        std::array<unsigned, Dim> signs;

        //results:
        Intersections intersections;
        Minimum minimum;


        RayTrianglesQuery(const BVHWrapper & wrapper, const Point & origin, const Point & direction) :
            wrapper(wrapper), origin(origin), direction(direction)
        {

            intersections::signs_and_inv_direction(direction, signs, inv_direction);

            minimum = Minimum{~0u, std::numeric_limits<Scalar>::max(), Point()};

        }
        bool intersectVolume(const typename BVH::Volume &volume)
        {
            Scalar p_min, p_max;
            return intersections::intersect_line_box<Point>(origin, inv_direction, signs, volume.min(), volume.max(), Scalar(0),  std::numeric_limits<Scalar>::max(), p_min, p_max);
        }

        bool intersectObject(const typename BVH::Object &object)
        {
            Triangle t = wrapper.indices(object);
            Point tuv;
            if(intersections::intersect_line_triangle<false>(origin
                    , direction
                    , wrapper.point(t[0])
                    , wrapper.point(t[1])
                    , wrapper.point(t[2])
                    , tuv))
            {
                intersections.emplace_back(Intersection{object, tuv});
            }
            return false; //never stop query
        }

        Scalar minimumOnVolume(const typename BVH::Volume &volume)
        {
            return std::get<0>(distances::line_box_distance(origin.transpose().eval(), direction.transpose().eval(), volume.min(), volume.max()));
        }

        Scalar minimumOnObject(const typename BVH::Object &object)
        {
            Triangle t = wrapper.indices(object);

            Scalar distance;
            Point tuv;
            std::tie(distance, tuv) = distances::line_triangle_distance(origin.transpose().eval()
                    , direction.transpose().eval()
                    , wrapper.point(t[0]).transpose().eval()
                    , wrapper.point(t[1]).transpose().eval()
                    , wrapper.point(t[2]).transpose().eval());

            if(distance < minimum.distance)
                minimum = Minimum{object, distance, tuv};

            return distance;

        }
};
}
