// src/components/ProfileModal.js
import React, { useState } from 'react';
import { updateUserProfile } from '../api';
import '../style/ProfileModal.css'; 

function ProfileModal({ userEmail, onClose }) {
    const [fullName, setFullName] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [msg, setMsg] = useState(null); // objet { type: 'success' | 'error', text: '' }

    const handleUpdate = async (e) => {
        e.preventDefault();
        setMsg(null);

        if(password && password !== confirm) {
            setMsg({ type: 'error', text: "Les mots de passe ne correspondent pas" }); 
            return;
        }

        try {
            await updateUserProfile(password, fullName);
            setMsg({ type: 'success', text: "Profil mis à jour avec succès !" });
            setPassword(''); 
            setConfirm('');
            // Fermer après 1.5 secondes pour que l'user voie le succès
            setTimeout(() => onClose(), 1500);
        } catch (e) { 
            setMsg({ type: 'error', text: "Erreur lors de la mise à jour." }); 
        }
    };

    // Fermer si on clique sur le fond gris
    const handleOverlayClick = (e) => {
        if (e.target.className === 'modal-overlay') onClose();
    };

    return (
        <div className="modal-overlay" onClick={handleOverlayClick}>
            <div className="modal-content">
                <button className="close-btn" onClick={onClose}>&times;</button>
                
                <h2>Paramètres</h2>
                <p>{userEmail}</p>
                
                <form onSubmit={handleUpdate}>
                    <div>
                        <label>Nom d'affichage</label>
                        <input 
                            type="text" 
                            placeholder="Votre prénom ou pseudo" 
                            value={fullName} 
                            onChange={e=>setFullName(e.target.value)} 
                        />
                    </div>
                    
                    <div>
                        <label>Nouveau mot de passe</label>
                        <input 
                            type="password" 
                            placeholder="Laisser vide si inchangé" 
                            value={password} 
                            onChange={e=>setPassword(e.target.value)} 
                        />
                    </div>
                    
                    {password && (
                        <div>
                            <label>Confirmer le mot de passe</label>
                            <input 
                                type="password" 
                                placeholder="Répétez le mot de passe" 
                                value={confirm} 
                                onChange={e=>setConfirm(e.target.value)} 
                            />
                        </div>
                    )}
                    
                    {msg && (
                        <div className={`status-msg ${msg.type}`}>
                            {msg.text}
                        </div>
                    )}
                    
                    <button type="submit" className="save-btn">Enregistrer les modifications</button>
                </form>
            </div>
        </div>
    );
}
export default ProfileModal;