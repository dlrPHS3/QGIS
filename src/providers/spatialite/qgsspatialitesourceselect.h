/***************************************************************************
                          qgspatialitesourceselect.h  -  description
                             -------------------
    begin                : Dec 2008
    copyright            : (C) 2008 by Sandro Furieri
    email                : a.furieri@lqt.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
#ifndef QGSSPATIALITESOURCESELECT_H
#define QGSSPATIALITESOURCESELECT_H
#include "ui_qgsdbsourceselectbase.h"
#include "qgisgui.h"
#include "qgsdbfilterproxymodel.h"
#include "qgsspatialitetablemodel.h"
#include "qgshelp.h"

#include <QThread>
#include <QMap>
#include <QList>
#include <QPair>
#include <QIcon>
#include <QFileDialog>

class QStringList;
class QTableWidgetItem;
class QPushButton;

/** \class QgsSpatiaLiteSourceSelect
 * \brief Dialog to create connections and add tables from SpatiaLite.
 *
 * This dialog allows the user to define and save connection information
 * for SpatiaLite/SQLite databases. The user can then connect and add
 * tables from the database to the map canvas.
 */
class QgsSpatiaLiteSourceSelect: public QDialog, private Ui::QgsDbSourceSelectBase
{
    Q_OBJECT

  public:

    /* Open file selector to add new connection */
    static bool newConnection( QWidget *parent );

    //! Constructor
    QgsSpatiaLiteSourceSelect( QWidget *parent, Qt::WindowFlags fl = QgisGui::ModalDialogFlags, bool embedded = false );

    ~QgsSpatiaLiteSourceSelect();
    //! Populate the connection list combo box
    void populateConnectionList();
    //! Determines the tables the user selected and closes the dialog
    void addTables();
    //! String list containing the selected tables
    QStringList selectedTables();
    //! Connection info (DB-path)
    QString connectionInfo();
    // Store the selected database
    void dbChanged();

  public slots:

    /** Connects to the database using the stored connection parameters.
     * Once connected, available layers are displayed.
     */
    void on_btnConnect_clicked();
    void buildQuery();
    void addClicked();
    void updateStatistics();
    //! Opens the create connection dialog to build a new connection
    void on_btnNew_clicked();
    //! Deletes the selected connection
    void on_btnDelete_clicked();
    void on_mSearchGroupBox_toggled( bool );
    void on_mSearchTableEdit_textChanged( const QString &text );
    void on_mSearchColumnComboBox_currentIndexChanged( const QString &text );
    void on_mSearchModeComboBox_currentIndexChanged( const QString &text );
    void on_cbxAllowGeometrylessTables_stateChanged( int );
    void setSql( const QModelIndex &index );
    void on_cmbConnections_activated( int );
    void setLayerType( const QString &table, const QString &column, const QString &type );
    void on_mTablesTreeView_clicked( const QModelIndex &index );
    void on_mTablesTreeView_doubleClicked( const QModelIndex &index );
    void treeWidgetSelectionChanged( const QItemSelection &selected, const QItemSelection &deselected );
    //!Sets a new regular expression to the model
    void setSearchExpression( const QString &regexp );

    void on_buttonBox_helpRequested() { QgsHelp::openHelp( QStringLiteral( "working_with_vector/supported_data.html#spatialite-layers" ) ); }

  signals:
    void connectionsChanged();
    void addDatabaseLayers( QStringList const &paths, QString const &providerKey );

  private:
    enum Columns
    {
      DbssType = 0,
      DbssDetail,
      DbssSql,
      DbssColumns,
    };

    typedef QPair< QString, QString > geomPair;
    typedef QList< geomPair > geomCol;

    // Set the position of the database connection list to the last
    // used one.
    void setConnectionListPosition();
    // Combine the table and column data into a single string
    // useful for display to the user
    QString fullDescription( const QString &table, const QString &column, const QString &type );
    // The column labels
    QStringList mColumnLabels;
    QString mSqlitePath;
    QStringList m_selectedTables;
    // Storage for the range of layer type icons
    QMap < QString, QPair < QString, QIcon > >mLayerIcons;
    //! Model that acts as datasource for mTableTreeWidget
    QgsSpatiaLiteTableModel mTableModel;
    QgsDatabaseFilterProxyModel mProxyModel;

    QString layerURI( const QModelIndex &index );
    QPushButton *mBuildQueryButton = nullptr;
    QPushButton *mAddButton = nullptr;
    QPushButton *mStatsButton = nullptr;
};

#endif // QGSSPATIALITESOURCESELECT_H
