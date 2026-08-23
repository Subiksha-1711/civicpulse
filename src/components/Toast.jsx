import { CheckCircle2, AlertCircle } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function Toast() {
  const { toast } = useApp();
  if (!toast) return null;
  return (
    <div className={`toast ${toast.type}`} role="status">
      {toast.type === 'error' ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
      <span>{toast.message}</span>
    </div>
  );
}
