// src/components/Sidebar.js
import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { 
    fetchChatIds, 
    togglePinChat, 
    deleteChatHistory, 
    deleteAllHistory 
} from '../api';

import ProfileModal from './ProfileModal';
import '../style/Sidebar.css';

// --- FONCTION UTILITAIRE : FORMATAGE DATE ---
const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('fr-FR', { month: 'short', day: 'numeric' }).format(date);
};

// --- COMPOSANT PRINCIPAL ---

function Sidebar({ userEmail, onLogout, onSelectChat, onNewChat, currentChatId, refreshCounter }) {
    const [chatList, setChatList] = useState([]);
    const [pinnedList, setPinnedList] = useState([]);
    // NOUVEAU: Stocke le mapping {chatId: {title: 'Mon Titre'}}
    const [chatDetails, setChatDetails] = useState({}); 
    const [loading, setLoading] = useState(false);
    
    // États pour l'interface
    const [activeMenuId, setActiveMenuId] = useState(null); 
    const [showProfile, setShowProfile] = useState(false);
    
    // Référence pour détecter le clic dehors
    const sidebarRef = useRef(null);

    // --- LOGIQUE DE CHARGEMENT ---
    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            // Supposons que fetchChatIds() retourne toujours {all_ids: [...], pinned_ids: [...]}
            const data = await fetchChatIds();
            const allIds = data.all_ids || [];
            const pinnedIds = data.pinned_ids || [];
            
            setChatList(allIds);
            setPinnedList(pinnedIds);

            // ⚠️ SIMULATION DES VRAIS TITRES
            // EN PRODUCTION, VOUS DEVEZ MODIFIER VOTRE API POUR QU'ELLE RETOURNE LE TITRE RÉEL
            // Ceci simule un titre plus pertinent que la simple date:
            const detailsMap = allIds.reduce((acc, chatId, index) => {
                let title = "Conversation non titrée";
                
                try {
                    // Pour la simulation, on utilise la date comme fallback ou pour trier
                    const parts = chatId.split('_');
                    const ts = parseInt(parts[parts.length - 1], 10);
                    
                    if (!isNaN(ts) && ts.toString().length >= 10) {
                        // Simuler des titres de sujet basés sur l'index (pour l'exemple)
                        if (index === 0) title = "Calcul de la somme en Python (Dernier)";
                        else if (index === 1) title = "Résumé des étapes du projet 2024";
                        else if (index === 2) title = "Explication de l'algorithme de tri";
                        else title = `Sujet du ${formatDate(ts)}` // Fallback si trop d'éléments
                    }
                } catch {}
                
                acc[chatId] = { title: title };
                return acc;
            }, {});
            setChatDetails(detailsMap);

        } catch (err) {
            console.error("Erreur de chargement de la sidebar:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Charger les données initiales et lors du refresh
    useEffect(() => {
        loadData();
    }, [refreshCounter, loadData]);
    
    // Fermer les menus si on clique ailleurs
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (sidebarRef.current && !sidebarRef.current.contains(event.target)) {
                setActiveMenuId(null);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);
    
    // --- ACTIONS ---

    const handlePin = async (e, chatId) => {
        e.stopPropagation();
        setActiveMenuId(null); 
        
        const isCurrentlyPinned = pinnedList.includes(chatId);
        
        try {
            await togglePinChat(chatId);
            
            // Mise à jour de l'état local
            setPinnedList(prev => 
                isCurrentlyPinned 
                    ? prev.filter(id => id !== chatId) 
                    : [chatId, ...prev]
            );
            
        } catch (err) {
            console.error(`Erreur d'épinglage du chat ${chatId}:`, err);
        }
    };

    const handleDelete = async (e, chatId) => {
        e.stopPropagation();
        setActiveMenuId(null); 
        
        if (window.confirm("Supprimer cette conversation définitivement ?")) {
            try {
                await deleteChatHistory(chatId);
                
                // Mise à jour des listes locales
                setChatList(prev => prev.filter(id => id !== chatId));
                setPinnedList(prev => prev.filter(id => id !== chatId));
                
                // Supprimer les détails du chat également
                setChatDetails(prev => {
                    const { [chatId]: _, ...rest } = prev;
                    return rest;
                });
                
                if (currentChatId === chatId) {
                    onNewChat();
                }
            } catch (err) {
                console.error(`Erreur suppression chat ${chatId}:`, err);
            }
        }
    };

    const handleDeleteAll = async () => {
        if (window.confirm("ATTENTION : Cela va effacer TOUT l'historique. Continuer ?")) {
            try {
                await deleteAllHistory();
                setChatList([]);
                setPinnedList([]);
                setChatDetails({}); // Vider les détails
                onNewChat();
            } catch (err) {
                console.error("Erreur suppression de tout l'historique:", err);
            }
        }
    };
    
    // --- SÉPARATION ET TRI DES LISTES (Optimisation avec useMemo) ---
    const { pinnedChats, recentChats } = useMemo(() => {
        const sortedChats = [...chatList];
        
        const pinned = sortedChats.filter(id => pinnedList.includes(id));
        const recent = sortedChats.filter(id => !pinnedList.includes(id));
        
        return { pinnedChats: pinned, recentChats: recent };
    }, [chatList, pinnedList]);


    // --- RENDU D'UN ÉLÉMENT DE LA LISTE ---
    const renderChatItem = (chatId) => {
        const isPinned = pinnedList.includes(chatId);
        const isActive = currentChatId === chatId;
        const isMenuOpen = activeMenuId === chatId;
        
        // NOUVEAU: Récupérer le titre SIGNIFICATIF
        const chatTitle = chatDetails[chatId]?.title || "Conversation"; 
        
        // Icône de bulle de conversation (par défaut)
        const chatIcon = (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        );

        // Icône épinglée
        const pinIcon = (
            <svg viewBox="0 0 24 24" fill="currentColor" className="pin-icon"><path d="M16 12V4H17V2H7V4H8V12L6 14V16H11.2V22H12.8V16H18V14L16 12Z"/></svg>
        );

        // Icône 3 points du menu
        const menuIcon = (
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/></svg>
        );
        
        const iconToUse = isPinned ? pinIcon : chatIcon;


        return (
            <div key={chatId} className={`nav-item-container ${isActive ? 'active' : ''}`}>
                <div 
                    className="nav-item" 
                    onClick={() => { onSelectChat(chatId); setActiveMenuId(null); }}
                >
                    <span className="icon">
                        {iconToUse}
                    </span>
                    
                    <span className="title">
                        {/* AFFICHE LE TITRE OU UN TITRE PAR DÉFAUT */}
                        {chatTitle} 
                    </span>
                </div>

                {/* Bouton Menu (3 points) */}
                <button 
                    className="menu-trigger" 
                    onClick={(e) => { 
                        e.stopPropagation(); 
                        setActiveMenuId(isMenuOpen ? null : chatId); 
                    }}
                >
                    {menuIcon}
                </button>

                {/* Menu Contextuel Flottant */}
                {isMenuOpen && (
                    <div className="context-menu" onClick={(e) => e.stopPropagation()}>
                        <button onClick={(e) => handlePin(e, chatId)}>
                            {isPinned ? 'Détacher' : 'Épingler'}
                        </button>
                        <button className="delete-btn" onClick={(e) => handleDelete(e, chatId)}>
                            Supprimer
                        </button>
                    </div>
                )}
            </div>
        );
    };


    return (
        <div className="sidebar" ref={sidebarRef}>
            {/* 1. Header (Nouveau Chat) */}
            <div className="sidebar-header">
                <button className="new-chat-btn" onClick={onNewChat}>
                    <span>Nouveau Chat</span> 
                </button>
            </div>

            {/* 2. Liste Scrollable */}
            <div className="sidebar-nav">
                
                {/* 2a. Section Épinglés */}
                {pinnedChats.length > 0 && (
                    <div className="nav-section">
                        <div className="section-label">Favoris</div>
                        {pinnedChats.map(renderChatItem)}
                    </div>
                )}

                {/* 2b. Section Récents */}
                <div className="nav-section">
                    <div className="section-label">Récents</div>
                    {loading ? (
                        <div className="loading-placeholder">Chargement des conversations...</div>
                    ) : chatList.length === 0 ? (
                        <div className="empty-state">Commencez une nouvelle conversation.</div>
                    ) : (
                        recentChats.map(renderChatItem)
                    )}
                </div>
            </div>

            {/* 3. Footer (Profil & Options) */}
            <div className="sidebar-footer">
                <button className="footer-item" onClick={() => setShowProfile(true)} title="Gérer le profil">
                    <div className="avatar-circle">{userEmail.charAt(0).toUpperCase()}</div>
                    <div className="footer-text">
                        <div className="user-name">Mon Compte</div>
                        <div className="user-email-sub">{userEmail}</div>
                    </div>
                </button>
                
                <div className="footer-actions">
                    <button className="icon-btn danger" onClick={handleDeleteAll} title="Tout supprimer">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                    <button className="icon-btn" onClick={onLogout} title="Se déconnecter">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                    </button>
                </div>
            </div>

            {/* Modale Profil */}
            {showProfile && <ProfileModal userEmail={userEmail} onClose={() => setShowProfile(false)} />}
        </div>
    );
}

export default Sidebar;