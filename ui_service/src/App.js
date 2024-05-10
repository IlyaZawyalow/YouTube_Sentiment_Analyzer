// App.js

import React, { useState, useEffect } from 'react';
import { parseVideo } from './api';
import { getComments } from './api';
import { Form, Button, Table } from 'react-bootstrap';
import 'chart.js/auto';
import { Pie } from 'react-chartjs-2';
import './App.css';

function App() {
  const [videoUrl, setVideoUrl] = useState('');
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showTable, setShowTable] = useState(false);
  const [pieChartData, setPieChartData] = useState(null);

  useEffect(() => {
    if (comments.length > 0) {
      const countPositive = comments.filter(comment => comment.sentiment === 'positive').length;
      const countNegative = comments.filter(comment => comment.sentiment === 'negative').length;
      const data = {
        labels: ['Positive', 'Negative'],
        datasets: [
          {
            data: [countPositive, countNegative],
            backgroundColor: [
              'rgba(75, 192, 192, 0.6)',
              'rgba(255, 99, 132, 0.6)'
            ],
            hoverBackgroundColor: [
              'rgba(75, 192, 192, 0.8)',
              'rgba(255, 99, 132, 0.8)'
            ]
          }
        ]
      };
      setPieChartData(data);
    }
  }, [comments]);

  const handleParse = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await parseVideo(videoUrl);
      if (data && data.video_id) {
        await fetchComments(data.video_id);
        setShowTable(true);
      } else {
        setError("Invalid YouTube URL");
        setShowTable(false);
      }
    } catch (error) {
      setError("An error occurred while parsing the video.");
      setShowTable(false);
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async (videoId) => {
    try {
      const data = await getComments(videoId);
      setComments(data.comments);
    } catch (error) {
      console.error("Error fetching comments:", error);
    }
  };

  return (
    <div className="container mt-5">
      <h1 className="mb-4">YouTube Sentiment Analyzer</h1>
      <Form className="d-flex mx-auto mb-3">
        <Form.Control
          type="text"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          placeholder="Enter YouTube video URL"
          className="me-2"
        />
        <Button className="custom-button" onClick={handleParse} disabled={loading}>
          Parse
        </Button>
      </Form>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {showTable && (
        <div className="table-container" style={{ maxHeight: '400px', overflowY: 'auto' }}>
          <Table striped bordered hover className="table-custom">
            <thead>
              <tr>
                <th>Text</th>
                <th>Sentiment</th>
              </tr>
            </thead>
            <tbody>
              {comments.map((comment, index) => (
                <tr key={index} className={comment.sentiment === 'negative' ? 'table-danger text-danger' : ''}>
                  <td>{comment.text}</td>
                  <td>{comment.sentiment}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
      {pieChartData && (
        <div className="pie-chart-container">
          <Pie data={pieChartData} className="custom-pie" /> {}
        </div>
      )}
    </div>
  );
}

export default App;
