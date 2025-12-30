from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# All BIDS entities in global order
STANDARD_ENTITY_ORDER = ['sub', 'ses', 'sample', 'task', 'acq', 'ce', 'trc', 'stain', 'rec', 'dir', 'run', 'mod', 'echo', 'flip', 'inv', 'mt', 'part', 'proc', 'space', 'split', 'recording', 'chunk', 'seg', 'res', 'den', 'label', 'desc']

# Map full entity names to their BIDS abbreviations
ENTITY_ABBREVIATIONS = {
    'subject': 'sub',
    'session': 'ses',
    'sample': 'sample',
    'task': 'task',
    'acquisition': 'acq',
    'ce': 'ce',
    'trc': 'trc',
    'stain': 'stain',
    'reconstruction': 'rec',
    'direction': 'dir',
    'run': 'run',
    'modality': 'mod',
    'echo': 'echo',
    'flip': 'flip',
    'inversion': 'inv',
    'mt': 'mt',
    'part': 'part',
    'processing': 'proc',
    'space': 'space',
    'split': 'split',
    'recording': 'recording',
    'chunk': 'chunk',
    'segment': 'seg',
    'resolution': 'res',
    'denoising': 'den',
    'label': 'label',
    'description': 'desc',
}




class BIDSPath:
    """
    A class representing a BIDS file path with its entities.
    Supports both standard and non-standard BIDS entities.
    """

    def __init__(self, root: Optional[Union[str, Path]] = None, **entities):
        """
        Initialize BIDSPath with entities.

        Args:
            root: Root BIDS directory (optional)
            **entities: BIDS entities as keyword arguments
        """
        self.root = Path(root) if root else None
        self.entities = dict(entities)

    def __repr__(self) -> str:
        entities_str = ', '.join(f"{k}='{v}'" for k, v in self.entities.items())
        return f"BIDSPath({entities_str})"

    def __str__(self) -> str:
        if self.root:
            return str(self.fpath)

        return self._build_filename()

    def __eq__(self, other) -> bool:
        if not isinstance(other, BIDSPath):
            return False
        return self.entities == other.entities and self.root == other.root

    def __getitem__(self, key: str) -> Any:
        """Get entity value by key."""
        return self.entities[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set entity value by key."""
        self.entities[key] = value

    def __contains__(self, key: str) -> bool:
        """Check if entity exists."""
        return key in self.entities

    def get(self, key: str, default: Any = None) -> Any:
        """Get entity value with default."""
        return self.entities.get(key, default)

    def copy(self) -> 'BIDSPath':
        """Create a copy of this BIDSPath."""
        return BIDSPath(root=self.root, **self.entities.copy())

    def update(self, **entities) -> 'BIDSPath':
        """Update entities and return a new BIDSPath."""
        new_path = self.copy()
        new_path.entities.update(entities)
        return new_path

    @property
    def subject(self) -> Optional[str]:
        """Get subject ID."""
        return self.entities.get('subject')

    @subject.setter
    def subject(self, value: str) -> None:
        """Set subject ID."""
        self.entities['subject'] = value

    @property
    def session(self) -> Optional[str]:
        """Get session ID."""
        return self.entities.get('session')

    @session.setter
    def session(self, value: str) -> None:
        """Set session ID."""
        self.entities['session'] = value

    @property
    def datatype(self) -> Optional[str]:
        """Get datatype."""
        return self.entities.get('datatype')

    @datatype.setter
    def datatype(self, value: str) -> None:
        """Set datatype."""
        self.entities['datatype'] = value

    @property
    def suffix(self) -> Optional[str]:
        """Get suffix."""
        return self.entities.get('suffix')

    @suffix.setter
    def suffix(self, value: str) -> None:
        """Set suffix."""
        self.entities['suffix'] = value

    @property
    def extension(self) -> Optional[str]:
        """Get file extension."""
        return self.entities.get('extension')

    @extension.setter
    def extension(self, value: str) -> None:
        """Set file extension."""
        self.entities['extension'] = value

    def _format_entity_value(self, key: str, value: Union[str, int]) -> str:
        """Format entity value according to BIDS conventions."""
        if key == 'subject':
            return f"sub-{value}"
        elif key == 'session':
            return f"ses-{value}"
        elif key == 'run':
            return f"run-{value:02d}" if isinstance(value, int) else f"run-{value}"
        else:
            return f"{key}-{value}"

    def _build_filename(self) -> str:
        """Build filename from entities."""
        parts = []

        # Process entities in BIDS standard order
        for entity in STANDARD_ENTITY_ORDER:
            entity_key = ENTITY_ABBREVIATIONS.get(entity, entity)
            # Check if the entity exists in our entities dictionary
            if entity_key in self.entities:
                value = self.entities[entity_key]
                # Format the entity-value pair
                formatted_entity = self._format_entity_value(entity_key, value)
                parts.append(formatted_entity)

        # Handle any non-standard entities
        for key in self.entities:
            if key not in STANDARD_ENTITY_ORDER and key not in ['suffix', 'extension', 'subject', 'session', 'run']:
                value = self.entities[key]
                formatted_entity = self._format_entity_value(key, value)
                parts.append(formatted_entity)

        # Add suffix if it exists
        if 'suffix' in self.entities:
            parts.append(self.entities['suffix'])

        # Join all parts with underscores
        filename = '_'.join(parts)

        # Add extension if it exists
        if 'extension' in self.entities:
            filename += self.entities['extension']

        return filename



    def _build_directory_path(self) -> Path:
        """Build directory path from entities."""
        if not self.root:
            raise ValueError("Root directory must be set to build full directory path")

        path_parts = [self.root]

        # Add subject directory
        if 'subject' in self.entities:
            subject_dir = f"sub-{self.entities['subject']}"
            path_parts.append(subject_dir)

        # Add session directory if specified
        if 'session' in self.entities:
            session_dir = f"ses-{self.entities['session']}"
            path_parts.append(session_dir)

        # Add datatype directory
        if 'datatype' in self.entities:
            path_parts.append(self.entities['datatype'])

        return Path(*path_parts)

    @property
    def fpath(self) -> Path:
        """Get full file path."""
        if not self.root:
            raise ValueError("Root directory must be set to get full file path")

        directory = self._build_directory_path()
        filename = self._build_filename()
        return directory / filename

    @property
    def dirname(self) -> Path:
        """Get directory path."""
        return self._build_directory_path()

    @property
    def basename(self) -> str:
        """Get filename."""
        return self._build_filename()


class BIDSLayout:
    """
    A BIDS layout manager that can generate file paths and query existing files.
    Supports both standard and non-standard BIDS entities.
    """

    def __init__(self, root_dir: Union[str, Path]):
        """
        Initialize BIDS layout with root directory.

        Args:
            root_dir: Path to the root BIDS directory
        """
        self.root_dir = Path(root_dir)


    def __hash__(self) -> int:
        """Hash function for BIDSLayout."""
        return hash(self.root_dir)

    def __repr__(self) -> str:
        """String representation of BIDSLayout."""
        return f"BIDSLayout(root_dir={self.root_dir})"

    def __eq__(self, other) -> bool:
        """Equality check for BIDSLayout."""
        if not isinstance(other, BIDSLayout):
            return False
        return self.root_dir == other.root_dir

    def _entities_from_input(self, entities_input: Union[Dict, BIDSPath]) -> Dict[str, Any]:
        """Convert input to entities dictionary."""
        if isinstance(entities_input, BIDSPath):
            return entities_input.entities.copy()
        elif isinstance(entities_input, dict):
            return entities_input.copy()
        else:
            raise TypeError("entities_input must be either Dict or BIDSPath")

    def _parse_filename(self, filename: str) -> Dict[str, str]:
        """Parse a BIDS filename to extract entities."""
        entities = {}

        # Remove extension
        entities["extension"] =  Path(filename).suffix
        name_without_ext = Path(filename).stem


        # Extract suffix (last part after final underscore)
        if '_' in name_without_ext:
            parts = name_without_ext.split('_')
            last_part = parts[-1]
            # make sure that the last part is not an entity (i.e., does not contain '-')
            if '-' not in last_part:
                entities['suffix'] = last_part
                entity_parts = parts[:-1]
            entity_parts = [name_without_ext]
        else:
            entity_parts = [name_without_ext]

        # Parse entities
        for part in entity_parts:
            if '-' in part:
                key, value = part.split('-', 1)
                if key == 'sub':
                    entities['subject'] = value
                elif key == 'ses':
                    entities['session'] = value
                elif key == 'run':
                    entities['run'] = value

                else:
                    # Support arbitrary entities
                    entities[key] = value

        return entities

    def generate_path(self, entities_input: Union[Dict[str, Any], BIDSPath], absolute: bool = True) -> BIDSPath:
        """
        Generate a BIDS-compliant file path from entities.

        Args:
            entities_input: Dictionary or BIDSPath containing BIDS entities

        Returns:
            BIDSPath object representing the BIDS file path
        """
        entities = self._entities_from_input(entities_input)
        return BIDSPath(root=self.root_dir, **entities)

    def query(self, entities_input: Optional[Union[Dict[str, Any], BIDSPath]] = None,
              **kwargs) -> List[BIDSPath]:
        """
        Query existing files that match the specified entities.

        Args:
            entities_input: Dictionary or BIDSPath containing BIDS entities to match
            **kwargs: Additional entities to match (merged with entities_input)

        Returns:
            List of BIDSPath objects matching the criteria
        """
        # Combine entities from input and kwargs
        if entities_input is not None:
            entities = self._entities_from_input(entities_input)
        else:
            entities = {}
        entities.update(kwargs)

        matches = []

        if not self.root_dir.exists():
            return matches

        # If subject is specified, limit search to that subject
        if 'subject' in entities:
            subject_dirs = [self.root_dir / f"sub-{entities['subject']}"]
        else:
            # Search all subject directories
            subject_dirs = [d for d in self.root_dir.iterdir()
                          if d.is_dir() and d.name.startswith('sub-')]

        for subject_dir in subject_dirs:
            if not subject_dir.exists():
                continue

            # Handle session directories
            if 'session' in entities:
                session_dirs = [subject_dir / f"ses-{entities['session']}"]
            else:
                # Check for session directories or use subject dir directly
                session_dirs = [d for d in subject_dir.iterdir()
                              if d.is_dir() and d.name.startswith('ses-')]
                if not session_dirs:
                    session_dirs = [subject_dir]

            for session_dir in session_dirs:
                if not session_dir.exists():
                    continue

                # Handle datatype directories
                if 'datatype' in entities:
                    datatype_dirs = [session_dir / entities['datatype']]
                else:
                    # Search all subdirectories
                    datatype_dirs = [d for d in session_dir.iterdir() if d.is_dir()]

                for datatype_dir in datatype_dirs:
                    if not datatype_dir.exists():
                        continue

                    # Search files in datatype directory
                    for file_path in datatype_dir.iterdir():
                        if file_path.is_file():
                            bids_path = self._path_to_bidspath(file_path)

                            # Check if file matches all specified entities
                            match = True
                            for key, value in entities.items():
                                if key == 'datatype':
                                    continue  # Already handled by directory structure
                                if key not in bids_path.entities or bids_path.entities[key] != value:
                                    match = False
                                    break

                            if match:
                                matches.append(bids_path)

        return sorted(matches, key=lambda x: str(x.fpath))

    def _path_to_bidspath(self, file_path: Path) -> BIDSPath:
        """Convert a file path to a BIDSPath object."""
        entities = {}

        # Extract from directory structure
        relative_path = file_path.relative_to(self.root_dir)
        parts = relative_path.parts

        for part in parts[:-1]:  # Exclude filename
            if part.startswith('sub-'):
                entities['subject'] = part[4:]
            elif part.startswith('ses-'):
                entities['session'] = part[4:]
            else:
                # Assume it's a datatype if it's not subject/session
                entities['datatype'] = part

        # Extract from filename
        filename_entities = self._parse_filename(file_path.name)
        entities.update(filename_entities)

        return BIDSPath(root=self.root_dir, **entities)

    def get_entities(self, file_path: Union[str, Path, BIDSPath]) -> Dict[str, Any]:
        """
        Extract BIDS entities from a file path.

        Args:
            file_path: Path to the BIDS file or BIDSPath object

        Returns:
            Dictionary of extracted entities
        """
        if isinstance(file_path, BIDSPath):
            return file_path.entities.copy()

        file_path = Path(file_path)
        bids_path = self._path_to_bidspath(file_path)
        return bids_path.entities

    def find_subjects(self) -> List[str]:
        """
        Find all unique subjects in the BIDS layout.

        Returns:
            List of unique subject IDs
        """
        subjects = set()

        if not self.root_dir.exists():
            return list(subjects)

        for subject_dir in self.root_dir.iterdir():
            if subject_dir.is_dir() and subject_dir.name.startswith('sub-'):
                subject_id = subject_dir.name[4:]
                subjects.add(subject_id)
        return sorted(subjects)

    def find_sessions(self, subject: str) -> List[str]:
        """
        Find all sessions for a given subject in the BIDS layout.

        Args:
            subject: Subject ID (e.g., '01')

        Returns:
            List of session IDs for the specified subject
        """
        sessions = set()
        subject_dir = self.root_dir / f"sub-{subject}"

        if not subject_dir.exists():
            return list(sessions)

        # Recursively find all files in the subject directory
        for file_path in subject_dir.rglob('*'):
            if file_path.is_file():
                # Extract entities from the file path
                bids_path = self._path_to_bidspath(file_path)

                # Check if this file belongs to the specified subject and has a session
                if (bids_path.entities.get('subject') == subject and
                    'session' in bids_path.entities):
                    sessions.add(bids_path.entities['session'])

        return sorted(sessions)

    def find_subjects_sessions(self) -> Dict[str, List[str]]:
        """
        Find all subjects and their sessions in the BIDS layout.

        Returns:
            Dictionary mapping subject IDs to lists of session IDs
        """
        subjects_sessions = {}

        for subject in self.find_subjects():
            sessions = self.find_sessions(subject)
            subjects_sessions[subject] = sessions

        return subjects_sessions


# Convenience function for backward compatibility
def generate_bids_path(root_dir: Union[str, Path],
                      entities: Union[Dict[str, Any], BIDSPath]) -> BIDSPath:
    """
    Generate a BIDS-compliant file path.

    Args:
        root_dir: Root BIDS directory
        entities: Dictionary or BIDSPath containing BIDS entities

    Returns:
        BIDSPath object representing the BIDS file path
    """
    layout = BIDSLayout(root_dir)
    return layout.generate_path(entities)
