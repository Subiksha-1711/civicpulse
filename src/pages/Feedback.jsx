import { useState } from 'react';
import { MessageSquareWarning } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import { Field, Button } from '../components/ui';
import { useApp } from '../context/AppContext';

export default function Feedback() {
  const [message, setMessage] = useState('');
  const [rating, setRating] = useState(0);
  const { showToast } = useApp();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim()) {
      showToast('Please enter your feedback', 'error');
      return;
    }
    setMessage('');
    setRating(0);
    showToast('Thank you for your feedback!');
  };

  return (
    <AppLayout title="Feedback">
      <div className="page-head">
        <h1>Feedback</h1>
        <p>Help us improve CivicPulse with your suggestions</p>
      </div>

      <div className="card card-pad" style={{ maxWidth: 620 }}>
        <div className="how-icon" style={{ marginBottom: 16 }}><MessageSquareWarning size={22} /></div>
        <form onSubmit={handleSubmit}>
          <Field label="How would you rate your experience?">
            <div className="flex gap-8">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  type="button"
                  key={n}
                  className={`btn btn-sm ${rating === n ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setRating(n)}
                >
                  {n}
                </button>
              ))}
            </div>
          </Field>
          <Field label="Your Feedback" required>
            <textarea
              className="textarea"
              placeholder="Tell us what you think, or suggest a new feature..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </Field>
          <Button type="submit">Submit Feedback</Button>
        </form>
      </div>
    </AppLayout>
  );
}
