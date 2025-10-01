'use client';

import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

interface Artifact {
  id: number;
  name: string;
  description: string;
  rarity: string;
  image_url: string | null;
  is_profile_modifier: boolean;
  background_effect: string | null;
  profile_effect: string | null;
  modifier_description: string | null;
}

interface ArtifactManagerProps {
  appliedArtifacts: Artifact[];
  availableArtifacts: Artifact[];
  token: string;
}

export function ArtifactManager({ appliedArtifacts, availableArtifacts, token }: ArtifactManagerProps) {
  const router = useRouter();
  const [loading, setLoading] = useState<number | null>(null);

  async function handleApply(e: FormEvent<HTMLFormElement>, artifactId: number) {
    e.preventDefault();
    setLoading(artifactId);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/me/apply-artifact/${artifactId}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        router.refresh();
      } else {
        const error = await response.json();
        alert(error.detail || 'Ошибка при применении артефакта');
      }
    } catch (error) {
      alert('Ошибка при применении артефакта');
    } finally {
      setLoading(null);
    }
  }

  async function handleUnapply(e: FormEvent<HTMLFormElement>, artifactId: number) {
    e.preventDefault();
    setLoading(artifactId);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/me/unapply-artifact/${artifactId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        router.refresh();
      } else {
        const error = await response.json();
        alert(error.detail || 'Ошибка при снятии артефакта');
      }
    } catch (error) {
      alert('Ошибка при снятии артефакта');
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="card">
      <h3>Артефакты-модификаторы</h3>
      <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem', lineHeight: 1.5 }}>
        Применяйте артефакты для усиления вашего профиля
      </p>

      {appliedArtifacts.length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <h4 style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>Применённые артефакты</h4>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {appliedArtifacts.map((artifact) => (
              <div
                key={artifact.id}
                className="card"
                style={{
                  background: 'rgba(0, 184, 148, 0.1)',
                  border: '1px solid rgba(0, 184, 148, 0.3)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <h5 style={{ margin: 0, fontSize: '1rem' }}>{artifact.name}</h5>
                    <span className="badge" style={{ marginTop: '0.5rem' }}>
                      {artifact.rarity}
                    </span>
                  </div>
                  {artifact.image_url && (
                    <img
                      src={artifact.image_url}
                      alt={artifact.name}
                      style={{ width: '50px', height: '50px', objectFit: 'cover', borderRadius: '8px' }}
                    />
                  )}
                </div>
                {artifact.modifier_description && (
                  <p style={{ color: '#00b894', fontSize: '0.9rem', marginTop: '0.75rem', fontStyle: 'italic' }}>
                    ✨ {artifact.modifier_description}
                  </p>
                )}
                <form onSubmit={(e) => handleUnapply(e, artifact.id)} style={{ marginTop: '1rem' }}>
                  <button
                    type="submit"
                    className="secondary"
                    style={{ width: '100%', fontSize: '0.9rem' }}
                    disabled={loading === artifact.id}
                  >
                    {loading === artifact.id ? 'Снимаем...' : 'Снять артефакт'}
                  </button>
                </form>
              </div>
            ))}
          </div>
        </div>
      )}

      {availableArtifacts.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h4 style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>Доступные модификаторы</h4>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {availableArtifacts.map((artifact) => (
              <div key={artifact.id} className="card" style={{ background: 'rgba(162, 155, 254, 0.05)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <h5 style={{ margin: 0, fontSize: '1rem' }}>{artifact.name}</h5>
                    <span className="badge" style={{ marginTop: '0.5rem' }}>
                      {artifact.rarity}
                    </span>
                  </div>
                  {artifact.image_url && (
                    <img
                      src={artifact.image_url}
                      alt={artifact.name}
                      style={{ width: '50px', height: '50px', objectFit: 'cover', borderRadius: '8px' }}
                    />
                  )}
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.75rem' }}>
                  {artifact.description}
                </p>
                {artifact.modifier_description && (
                  <p
                    style={{
                      color: '#00b894',
                      fontSize: '0.9rem',
                      marginTop: '0.5rem',
                      fontStyle: 'italic'
                    }}
                  >
                    ✨ {artifact.modifier_description}
                  </p>
                )}
                <form onSubmit={(e) => handleApply(e, artifact.id)} style={{ marginTop: '1rem' }}>
                  <button
                    type="submit"
                    className="primary"
                    style={{ width: '100%', fontSize: '0.9rem' }}
                    disabled={loading === artifact.id}
                  >
                    {loading === artifact.id ? 'Применяем...' : 'Применить артефакт'}
                  </button>
                </form>
              </div>
            ))}
          </div>
        </div>
      )}

      {availableArtifacts.length === 0 && appliedArtifacts.length === 0 && (
        <p style={{ color: 'var(--text-muted)', marginTop: '1.5rem', textAlign: 'center' }}>
          У вас пока нет артефактов-модификаторов. Выполняйте миссии, чтобы получить их!
        </p>
      )}
    </div>
  );
}
