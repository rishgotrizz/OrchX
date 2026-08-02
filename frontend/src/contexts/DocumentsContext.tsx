"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as DocTypes from '@/lib/types/document';
import { DocumentsRepository } from '@/lib/repositories/DocumentsRepository';
import { QueryKeys } from '@/lib/repositories/QueryKeys';
import { mockProjects, mockFolders, mockDocuments } from '@/lib/mock-data/documents';

export interface DocumentsState {
  documents: DocTypes.OrchXDocument[];
  projects: any[];
  folders: any[];
  session: DocTypes.DocumentSession;
  setSession: React.Dispatch<React.SetStateAction<DocTypes.DocumentSession>>;
  updateDocument: (id: string, content: string) => void;
  createDocument: (title: string, collectionId: string, initialContent?: string) => void;
  deleteDocument: (id: string) => void;
  isLoading: boolean;
  error: Error | null;
}

const DocumentsContext = createContext<DocumentsState | undefined>(undefined);

export function DocumentsProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [userCreatedDocs, setUserCreatedDocs] = useState<DocTypes.OrchXDocument[]>([]);

  const [session, setSession] = useState<DocTypes.DocumentSession>({
    projectId: 'proj-1',
    folderId: null,
    activeTabId: 'doc-1',
    tabs: [
      { id: 'doc-1', documentId: 'doc-1', isDirty: false, isPinned: true, scrollPosition: 0 }
    ],
    splitMode: 'none',
    splitSecondaryTabId: null,
  });

  const { data: rawDocuments, isLoading, error } = useQuery({
    queryKey: QueryKeys.documents.all,
    queryFn: DocumentsRepository.getAll
  });

  // Combine query docs/mock docs with user created docs
  const baseDocs = (rawDocuments && rawDocuments.length > 0) ? rawDocuments : mockDocuments;
  const documents = [...userCreatedDocs, ...baseDocs.filter(b => !userCreatedDocs.some(u => u.id === b.id))];

  const updateMutation = useMutation({
    mutationFn: ({ id, content }: { id: string; content: string }) => DocumentsRepository.update(id, { content }),
    onMutate: async ({ id, content }) => {
      await queryClient.cancelQueries({ queryKey: QueryKeys.documents.all });
      const previousDocs = queryClient.getQueryData<DocTypes.OrchXDocument[]>(QueryKeys.documents.all);
      
      queryClient.setQueryData<DocTypes.OrchXDocument[]>(QueryKeys.documents.all, old => {
        if (!old) return old;
        return old.map(d => d.id === id ? { ...d, content, updatedAt: new Date().toISOString() } : d);
      });
      
      return { previousDocs };
    },
    onError: (err, newDoc, context) => {
      if (context?.previousDocs) {
        queryClient.setQueryData(QueryKeys.documents.all, context.previousDocs);
      }
    },
  });

  const updateDocument = (id: string, content: string) => {
    setUserCreatedDocs(prev => prev.map(d => d.id === id ? { ...d, content, updatedAt: new Date().toISOString() } : d));
    updateMutation.mutate({ id, content });
    
    setSession(prev => ({
      ...prev,
      tabs: prev.tabs.map(t => t.documentId === id ? { ...t, isDirty: true } : t)
    }));
  };

  const createDocument = (title: string, collectionId: string, initialContent?: string) => {
    const newDocId = `doc-user-${Date.now()}`;
    const newDoc: DocTypes.OrchXDocument = {
      id: newDocId,
      title: title.trim() || "Untitled Specification",
      type: "specification",
      version: 1,
      status: "draft",
      content: initialContent || `# ${title}\n\nStart writing your project specification...`,
      tags: [collectionId.toLowerCase()],
      author: "User",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    setUserCreatedDocs(prev => [newDoc, ...prev]);

    setSession(prev => ({
      ...prev,
      activeTabId: newDocId,
      tabs: [...prev.tabs, { id: newDocId, documentId: newDocId, isDirty: false, isPinned: false, scrollPosition: 0 }]
    }));
  };

  const deleteDocument = (id: string) => {
    setUserCreatedDocs(prev => prev.filter(d => d.id !== id));
    setSession(prev => ({
      ...prev,
      tabs: prev.tabs.filter(t => t.documentId !== id),
      activeTabId: prev.activeTabId === id ? (prev.tabs.find(t => t.documentId !== id)?.documentId || '') : prev.activeTabId
    }));
  };

  const state: DocumentsState = {
    documents,
    projects: mockProjects,
    folders: mockFolders,
    session,
    setSession,
    updateDocument,
    createDocument,
    deleteDocument,
    isLoading,
    error: error as Error | null,
  };

  return (
    <DocumentsContext.Provider value={state}>
      {children}
    </DocumentsContext.Provider>
  );
}

export function useDocumentsContext() {
  const context = useContext(DocumentsContext);
  if (!context) throw new Error('useDocumentsContext must be used within a DocumentsProvider');
  return context;
}
