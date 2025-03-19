import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterPlot } from 'recharts';

const data = [
  {
    player: "Shubman Gill",
    span: "2020-2025",
    matches: 47,
    runs: 2459,
    average: 61.47,
    strikeRate: 102.28,
    hundreds: 6,
    fifties: 15,
    boundaries: 333
  },
  {
    player: "V Kohli",
    span: "2020-2025",
    matches: 54,
    runs: 2302,
    average: 50.04,
    strikeRate: 94.77,
    hundreds: 7,
    fifties: 17,
    boundaries: 240
  },
  {
    player: "SS Iyer",
    span: "2020-2025",
    matches: 47,
    runs: 2048,
    average: 53.89,
    strikeRate: 101.33,
    hundreds: 5,
    fifties: 13,
    boundaries: 250
  },
  {
    player: "KG Sharma",
    span: "2020-2025",
    matches: 46,
    runs: 2043,
    average: 49.82,
    strikeRate: 114.19,
    hundreds: 4,
    fifties: 14,
    boundaries: 323
  },
  {
    player: "KL Rahul",
    span: "2020-2025",
    matches: 53,
    runs: 1974,
    average: 50.61,
    strikeRate: 90.50,
    hundreds: 4,
    fifties: 13,
    boundaries: 200
  }
];

const performanceMetrics = [
  { name: 'Average > 50', count: data.filter(d => d.average > 50).length },
  { name: 'SR > 100', count: data.filter(d => d.strikeRate > 100).length },
  { name: '5+ Hundreds', count: data.filter(d => d.hundreds >= 5).length },
  { name: '10+ Fifties', count: data.filter(d => d.fifties >= 10).length }
];

export default function CricketDashboard() {
  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold mb-4">Cricket Performance Analysis Dashboard</h1>
      
      {/* Top Performers Card */}
      <Card>
        <CardHeader>
          <CardTitle>Top 5 Run Scorers (2020-2025)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="player" angle={-45} textAnchor="end" height={60} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="runs" fill="#8884d8" name="Runs Scored" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Performance Comparison Card */}
      <Card>
        <CardHeader>
          <CardTitle>Average vs Strike Rate Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="player" angle={-45} textAnchor="end" height={60} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="average" stroke="#8884d8" name="Batting Average" />
                <Line type="monotone" dataKey="strikeRate" stroke="#82ca9d" name="Strike Rate" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics Card */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Metrics Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceMetrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#82ca9d" name="Number of Players" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Key Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-4 space-y-2">
            <li>Shubman Gill leads the run-scoring charts with 2459 runs at an impressive average of 61.47</li>
            <li>V Kohli has the most centuries (7) in this period</li>
            <li>Three players maintain an average above 50: Gill, Kohli, and Iyer</li>
            <li>KG Sharma has the best strike rate among top 5 run-scorers (114.19)</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}