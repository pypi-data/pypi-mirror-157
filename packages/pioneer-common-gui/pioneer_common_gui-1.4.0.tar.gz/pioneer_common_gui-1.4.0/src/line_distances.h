/*
 * line_distances.h
 *
 *  Created on: Apr 24, 2018
 *      Author: Maxime Lemonnier
 */

#pragma once

#include "traits.h"
#include "line_intersections.h"
#include <iostream>
namespace distances
{
    template <typename Point>
    Point line_point_vector(const Point & origin, const Point & direction, const Point & point, scalar_t<Point> & p)
    {
        Point v = point - origin;
        p = v.dot(direction);
        return v - p * direction;
    }
    template <typename Point>
    decltype(auto) line_point_distance(const Point & origin, const Point & direction, const Point & point, scalar_t<Point> & p)
    {
        auto v = line_point_vector(origin, direction, point, p);
        return std::sqrt(v.dot(v));
    }
    template <typename Point>
    decltype(auto) line_point_distance(const Point & origin, const Point & direction, const Point & point)
    {
        scalar_t<Point> p;
        return line_point_distance(origin, direction, p);
    }

    /* Line line distance minimizer :
    // https://math.stackexchange.com/a/1235328
    // Let v(t) = v0 + t * v1  and w(u) = w0 + u * w1
    // Since the minimum distance is along a vector perpendicular to both v1 and w1, we must find s, so that
    // w − v = s * v1 × w1, and thus, we must solve
    // s * v1 × w1 + t * v1 − u * w1 = w0 − v0 for (s, t, u), which can be written in matrix form
    // [(v1 x w1)_x v1_x, w1_x] [ s] = [(w0-v0)_x]
    // [(v1 x w1)_y v1_y, w1_y] [ t] = [(w0-v0)_y]
    // [(v1 x w1))z v1_z, w1_z] [-u] = [(w0-v0)_z]
    */

    template <typename Point, typename S>
    Point line_line_distance(const Point & origin0, const Point & origin1, const S & solver)
    {
        Point stu = solver.solve(origin1 - origin0);
        stu[2] = -stu[2]; //remember, we solved for -u
        return stu;
    }
    template <typename Point>
    decltype(auto) line_line_distance_matrix(const Point & direction0, const Point & direction1, scalar_t<Point> threshold)
    {
        Point n = direction0.cross(direction1);
        if (n.dot(n) < threshold) //too parallel?
            throw std::invalid_argument("");

        Eigen::Matrix<scalar_t<Point>, 3, 3> A;
        A.col(0) = n;
        A.col(1) = direction0;
        A.col(2) = direction1;
        return A;
    }

    /*
     * computes distance between two lines
     * \return a 3d vector containing s (the minimum distance), t (parameter on line 0), u (parameter on line 1)
     */
    template <typename Point>
    Point line_line_distance(const Point & origin0, const Point & direction0, const Point & origin1, const Point & direction1, scalar_t<Point> threshold = std::numeric_limits<scalar_t<Point>>::epsilon())
    {
        static_assert(n_coords<Point>::value == 3u, "Only 3D points are supported.");

        try
        {
            auto S = line_line_distance_matrix(direction0, direction1, threshold).householderQr();
            return line_line_distance(origin0, origin1, S);
        }
        catch(const std::invalid_argument & e)
        {
            scalar_t<Point> t;
            auto d = line_point_distance(origin0, direction0, origin1, t);
            return Point(d, t, 0);
        }
    }

    /*
     * Minimum distance from a line to an axis-aligned box
     *
     * \param origin line's origin
     * \param direcion line's direction
     * \param min box's min corner
     * \param max box's max corner
     * \param threshold numerical precision threshold (value under which a number can be considered zero)
     * \return tuple with minimum distance (a scalar), line parameter at which the minimum point is (a scalar), point on box where the minimum is
     */
    template <typename Point>
    std::tuple<scalar_t<Point>, scalar_t<Point>, Point> line_box_distance(const Point & origin, const Point & direction, const Point & min, const Point & max, scalar_t<Point> threshold = std::numeric_limits<scalar_t<Point>>::epsilon())
    {
        typedef scalar_t<Point> Scalar;
        constexpr size_t Dim = n_coords<Point>::value;


        bool result;
        Scalar p_min, p_max;
        std::tie(result, p_min, p_max) = intersections::intersect_line_box<Point>(origin, direction, min, max, -std::numeric_limits<Scalar>::max(), std::numeric_limits<Scalar>::max());
        if(result)
        {
            Scalar u = fabs(p_min) < fabs(p_max) ? p_min : p_max;
            return std::make_tuple(Scalar(0), u, Point(origin + direction * u));
        }

        Scalar min_dist = std::numeric_limits<Scalar>::max();
        Scalar u_min;

        const Point & extents = max - min;
        Point box_point;
        Point box_edge_direction;
        Point box_edge_origin;
        auto update_result = [&](Scalar dist, Scalar u, auto get_point_point)
        {
            if(dist < min_dist)
            {
                min_dist = dist;
                u_min = u;
                box_point = get_point_point();
            }
        };

        //Try all 12 line line distance combinations, and fall back to point-line distance if the point of minimal distance outreach box's edge
        //There are only 3 possible box directions: (1,0,0), (0,1,0), (0,0,1), so we have 3 different line_line_distance_matrix()
        for(size_t d = 0; d < Dim; d++)
        {
            //the two other dimensions of interest:
            size_t d0 = (d+1)%Dim;
            size_t d1 = (d+2)%Dim;

            box_edge_direction[d]   = 1;
            box_edge_direction[d0]  = box_edge_direction[d1] = 0;
            box_edge_origin[d] = min[d];
            auto for_each_origin_of_interest = [&](auto f)
            {
                for(size_t i = 0; i < 2; i++)
                {
                    box_edge_origin[d0] = i > 0 ? max[d0] : min[d0];
                    for(size_t j = 0; j < 2; j++)
                    {
                        box_edge_origin[d1] = j > 0 ? max[d1] : min[d1];
                        f(box_edge_origin);
                    }
                }
            };
            try
            {
                auto S = line_line_distance_matrix(box_edge_direction, direction, std::numeric_limits<Scalar>::epsilon()).householderQr();
                for_each_origin_of_interest([&](const auto & box_edge_origin)
                {
                    auto stu = line_line_distance(box_edge_origin, origin, S);

                    if(stu[1] < 0)
                    {
                        const Scalar d = line_point_distance(origin, direction, box_edge_origin, stu[2]);
                        update_result(d, stu[2], [&](){return box_edge_origin;});
                    }
                    else if (stu[1] > extents[d])
                    {
                        Point box_line_end = box_edge_origin;
                        box_line_end[d] = max[d];
                        const Scalar d = line_point_distance(origin, direction, box_line_end, stu[2]);
                        update_result(d, stu[2], [&](){return box_line_end;});
                    }
                    else
                    {
                        update_result(std::fabs(stu[0]), stu[2], [&](){return box_edge_origin + box_edge_direction * stu[2];});
                    }
                });
            }
            catch(const std::invalid_argument & e)
            {
                //lines parallel!
                for_each_origin_of_interest([&](const auto & box_edge_origin)
                {
                    Scalar u;
                    const Scalar d = line_point_distance(origin, direction, box_edge_origin, u);
                    update_result(d, u, [&](){return box_edge_origin;});
                });
            }
        }
        return std::make_tuple(min_dist, u_min, box_point);
    }


    /*
     * Minimum distance from a line to a triangle
     *
     * \param origin line's origin
     * \param direcion line's direction
     * \param v0 triangle first point
     * \param v1 triangle second point
     * \param v2 triangle third point
     * \param threshold numerical precision threshold (value under which a number can be considered zero)
     * \return tuple with minimum distance (a scalar), and a point containing t, u and v coordinates (\see intersect_line_triangle())
     */
    template <typename Point>
    std::tuple<scalar_t<Point>, Point> line_triangle_distance(const Point & origin, const Point & direction, const Point & v0, const Point & v1, const Point & v2, scalar_t<Point> threshold = std::numeric_limits<scalar_t<Point>>::epsilon())
    {
        typedef scalar_t<Point> Scalar;

        Point tuv;
        bool result = intersections::intersect_line_triangle<false>(origin, direction, v0, v1, v2, tuv);
        if(result)
        {
            return std::make_tuple(Scalar(0), tuv);
        }

        Scalar min_dist = std::numeric_limits<Scalar>::max();

        auto update_result = [&](Scalar dist, auto get_tuv)
        {
            if(dist < min_dist)
            {
                min_dist = dist;
                tuv = get_tuv();
            }
        };

        const Point * origins[3] = {&v0, &v1, &v2};

        //Try all 3 line line distance combinations, and fall back to point-line distance if the point of minimal distance outreach triangle's edge
        for(size_t e = 0; e < 3u; e++)
        {
            size_t next_e = (e+1)%3u;
            const Point & edge_origin = *(origins[e]);
            Scalar u = e == 0 ? 1 : 0;
            Scalar v = e == 1 ? 1 : 0;
            const Point & edge_end = *(origins[next_e]);
            Point edge_direction = (edge_end - edge_origin);
            Scalar norm = std::sqrt(edge_direction.dot(edge_direction));
            edge_direction /= norm;
            auto stu = line_line_distance(edge_origin, edge_direction, origin, direction);


            if(stu[1] < 0)
            {
                const Scalar d = line_point_distance(origin, direction, edge_origin, stu[2]);
                update_result(d, [&](){return Point(stu[1], u, v);});
            }
            else if (stu[1] <= 1) // if stu[1] > 1, then another edge test will have stu[1] < 0 since an edge origin is another edge's end
            {
                switch(e)
                {
                    case 0 : u = stu[1];     v = 1 - stu[1]; break;
                    case 1 : u = 0;          v = stu[1];     break;
                    case 2 : u = 1 - stu[1]; v = 0;          break;
                }

                update_result(std::fabs(stu[0]), [&](){return Point(stu[2], u / norm, v / norm);});
            }
        }
        return std::make_tuple(min_dist, tuv);
    }
}
