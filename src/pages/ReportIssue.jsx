import { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { LocateFixed, Upload, X, Plus, ChevronRight } from 'lucide-react';
import AppLayout from '../components/AppLayout';
import { Field, Button } from '../components/ui';
import { CATEGORIES, SUBCATEGORIES, LOCATIONS, ISSUE_IMAGES } from '../data/constants';
import { useApp } from '../context/AppContext';

const API_BASE_URL = 'http://localhost:5000';

export default function ReportIssue() {
  const [form, setForm] = useState({
    category: '', subcategory: '', description: '', locationName: '', latitude: '', longitude: '', additionalInfo: '',
  });
  const [photos, setPhotos] = useState([]);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef(null);
  const { addIssue, showToast, user } = useApp();
  const navigate = useNavigate();

  const subcategoryOptions = form.category ? SUBCATEGORIES[form.category] || [] : [];

  const handleUseLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setForm((f) => ({
            ...f,
            latitude: pos.coords.latitude.toFixed(4),
            longitude: pos.coords.longitude.toFixed(4),
            locationName: f.locationName || 'Current Location',
          }));
          showToast('Location detected successfully');
        },
        () => {
          const loc = LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)];
          setForm((f) => ({ ...f, latitude: loc.lat.toFixed(4), longitude: loc.lng.toFixed(4), locationName: f.locationName || loc.name }));
          showToast('Using approximate location', 'error');
        }
      );
    } else {
      const loc = LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)];
      setForm((f) => ({ ...f, latitude: loc.lat.toFixed(4), longitude: loc.lng.toFixed(4), locationName: f.locationName || loc.name }));
    }
  };

  const handleFiles = (files) => {
    const arr = Array.from(files).slice(0, 5 - photos.length);
    arr.forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => setPhotos((p) => [...p, { id: Date.now() + Math.random(), url: e.target.result }]);
      reader.readAsDataURL(file);
    });
  };

  const removePhoto = (id) => setPhotos((p) => p.filter((ph) => ph.id !== id));

  const validate = () => {
    const errs = {};
    if (!form.category) errs.category = 'Category is required';
    if (!form.subcategory) errs.subcategory = 'Subcategory is required';
    if (!form.description.trim() || form.description.trim().length < 10) errs.description = 'Please provide a description of at least 10 characters';
    if (!form.locationName.trim()) errs.locationName = 'Location is required';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) {
      showToast('Please fix the errors in the form', 'error');
      return;
    }
    setSubmitting(true);

    const loc = LOCATIONS.find((l) => l.name === form.locationName) || LOCATIONS[0];
    const latitude = form.latitude ? parseFloat(form.latitude) : loc.lat;
    const longitude = form.longitude ? parseFloat(form.longitude) : loc.lng;

    try {
      const res = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: form.description,
          latitude,
          longitude,
        }),
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();
      console.log('CivicPulse API response:', data); // keep this while testing, remove later

      // NOTE: field names below (classification, severity, issue_detection, etc.)
      // are based on the doc description of api.py. If your actual JSON keys
      // differ, adjust the data.xxx paths below to match.
      const newIssue = {
        id: data?.issue_detection?.issue_id || `ISSUE-2024-${String(Date.now()).slice(-4)}`,
        title: `${data?.classification?.subcategory || form.subcategory} reported on ${form.locationName}`,
        description: form.description,
        category: data?.classification?.category || form.category,
        subcategory: data?.classification?.subcategory || form.subcategory,
        location: form.locationName,
        latitude,
        longitude,
        status: 'Open',
        priority: data?.severity?.label || 'Medium',
        reportedBy: user?.name || 'You',
        reportedAt: new Date().toISOString(),
        image: photos[0]?.url || ISSUE_IMAGES[Math.floor(Math.random() * ISSUE_IMAGES.length)],
        images: photos.length ? photos.map((p) => p.url) : [ISSUE_IMAGES[0]],
        relatedComplaints: 1,
        clusterId: data?.issue_detection?.issue_id || null,
        aiConfidence: data?.issue_detection?.confidence || 0,
        additionalInfo: form.additionalInfo,
        aiDecision: data?.issue_detection?.decision, // NEW_ISSUE / RELATED_ISSUE / DUPLICATE_ISSUE
        department: data?.classification?.department,
        rawApiResponse: data, // handy for debugging in the issue detail page
      };

      addIssue(newIssue);
      showToast('Issue submitted successfully!');
      navigate(`/issues/${newIssue.id}`);
    } catch (err) {
      console.error('Failed to submit to CivicPulse API:', err);
      showToast('Could not reach CivicPulse backend. Is it running?', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppLayout title="Report an Issue">
      <div className="breadcrumb">
        <Link to="/dashboard">Home</Link> <ChevronRight size={13} /> <span>Report an Issue</span>
      </div>
      <div className="page-head">
        <h1>Report an Issue</h1>
        <p>Submit a civic issue with photos and location details</p>
      </div>

      <form onSubmit={handleSubmit} noValidate style={{ maxWidth: 780 }}>
        <div className="card card-pad" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0 }}>Issue Details</h3>
          <div className="field-row">
            <Field label="Category" required error={errors.category}>
              <select
                className={`select ${errors.category ? 'input-error' : ''}`}
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value, subcategory: '' })}
              >
                <option value="">Select Category</option>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </Field>
            <Field label="Subcategory" required error={errors.subcategory}>
              <select
                className={`select ${errors.subcategory ? 'input-error' : ''}`}
                value={form.subcategory}
                onChange={(e) => setForm({ ...form, subcategory: e.target.value })}
                disabled={!form.category}
              >
                <option value="">Select Subcategory</option>
                {subcategoryOptions.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </Field>
          </div>
          <Field label="Description" required error={errors.description}>
            <textarea
              className={`textarea ${errors.description ? 'input-error' : ''}`}
              placeholder="Describe the issue in detail..."
              maxLength={500}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
            <div className="muted text-sm" style={{ textAlign: 'right', marginTop: 4 }}>{form.description.length}/500</div>
          </Field>
        </div>

        <div className="card card-pad" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0 }}>Location</h3>
          <Button type="button" variant="primary" size="sm" onClick={handleUseLocation} style={{ marginBottom: 16 }}>
            <LocateFixed size={15} /> Use Current Location
          </Button>
          <div className="location-grid">
            <div>
              <Field label="Location Name" required error={errors.locationName}>
                <input
                  list="location-suggestions"
                  className={`input ${errors.locationName ? 'input-error' : ''}`}
                  placeholder="e.g. MG Road, Civil Lines"
                  value={form.locationName}
                  onChange={(e) => setForm({ ...form, locationName: e.target.value })}
                />
                <datalist id="location-suggestions">
                  {LOCATIONS.map((l) => <option key={l.name} value={l.name} />)}
                </datalist>
              </Field>
              <div className="field-row">
                <Field label="Latitude">
                  <input className="input" placeholder="11.0168" value={form.latitude} onChange={(e) => setForm({ ...form, latitude: e.target.value })} />
                </Field>
                <Field label="Longitude">
                  <input className="input" placeholder="76.9558" value={form.longitude} onChange={(e) => setForm({ ...form, longitude: e.target.value })} />
                </Field>
              </div>
            </div>
            <div className="map-preview">
              {form.latitude && form.longitude && (
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div className="pin" style={{ width: 26, height: 26, borderRadius: '50% 50% 50% 0', transform: 'rotate(-45deg)', background: '#22c55e', border: '2px solid white' }} />
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="card card-pad" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0 }}>Photos</h3>
          <div className="upload-box" onClick={() => fileInputRef.current?.click()} role="button" tabIndex={0}>
            <Upload size={26} style={{ marginBottom: 8 }} />
            <div>Click to upload or drag and drop</div>
            <div className="text-sm">PNG, JPG up to 5MB (max 5 photos)</div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              hidden
              onChange={(e) => handleFiles(e.target.files)}
            />
          </div>
          {photos.length > 0 && (
            <div className="photo-preview-grid">
              {photos.map((p) => (
                <div key={p.id} className="photo-preview">
                  <img src={p.url} alt="Uploaded preview" />
                  <button type="button" onClick={() => removePhoto(p.id)} aria-label="Remove photo"><X size={12} /></button>
                </div>
              ))}
              {photos.length < 5 && (
                <div className="photo-preview upload-box" style={{ padding: 0 }} onClick={() => fileInputRef.current?.click()}>
                  <Plus size={20} />
                </div>
              )}
            </div>
          )}
        </div>

        <div className="card card-pad" style={{ marginBottom: 20 }}>
          <h3 style={{ marginTop: 0 }}>Additional Information <span className="muted text-sm">(Optional)</span></h3>
          <Field>
            <textarea
              className="textarea"
              placeholder="E.g. Nearby landmark, street name, etc."
              value={form.additionalInfo}
              onChange={(e) => setForm({ ...form, additionalInfo: e.target.value })}
            />
          </Field>
        </div>

        <Button type="submit" className="btn-block" disabled={submitting}>
          {submitting ? 'Submitting...' : 'Submit Issue'}
        </Button>
      </form>
    </AppLayout>
  );
}