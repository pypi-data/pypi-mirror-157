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
struct RayPointsQuery
{
    static constexpr size_t Dim = BVHWrapper::Dim;
    typedef typename BVHWrapper::Point Point;
    typedef typename BVHWrapper::ShapeIndices PointIndex;
    typedef scalar_t<Point> Scalar;
    typedef scalar_t<PointIndex> Index;

    struct Minimum
    {
            typename BVH::Object id;
            Scalar distance;
            Scalar t;
    };

    const BVHWrapper & wrapper;
    const Point origin;
    const Point direction;
    Point inv_direction;
    std::array<unsigned, Dim> signs;

    //results:
    Minimum minimum;


    RayPointsQuery(const BVHWrapper & wrapper, const Point & origin, const Point & direction) :
        wrapper(wrapper), origin(origin), direction(direction)
    {

        intersections::signs_and_inv_direction(direction, signs, inv_direction);

        minimum = Minimum{~0u, std::numeric_limits<Scalar>::max(), std::numeric_limits<Scalar>::max()};

    }
    bool intersectVolume(const typename BVH::Volume &volume)
    {
        Scalar p_min, p_max;
        return intersections::intersect_line_box<Point>(origin, inv_direction, signs, volume.min(), volume.max(), Scalar(0),  std::numeric_limits<Scalar>::max(), p_min, p_max);
    }

    Scalar minimumOnVolume(const typename BVH::Volume &volume)
    {
        return std::get<0>(distances::line_box_distance(origin.transpose().eval(), direction.transpose().eval(), volume.min(), volume.max()));
    }

    Scalar minimumOnObject(const typename BVH::Object &object)
    {
        Scalar distance;
        Scalar t;

        PointIndex index = wrapper.indices(object);
        distance = distances::line_point_distance(origin
                , direction
                , Point(wrapper.point(index[0])), t);

        if(distance < minimum.distance)
            minimum = Minimum{object, distance, t};

        return distance;

    }
};
}
